import streamlit as st
import time
from agents.video_agent import VideoAgent
from database import save_video_job, get_video_history, update_video_job_status, get_connection
from ui.components import (
    premium_header, safe_action_wrapper, render_job_controls, 
    render_enhanced_table, confirm_action
)
import pandas as pd

def render_video_studio():
    premium_header("🎬 Video Studio", "Generate cinematic AI videos for your campaigns using state-of-the-art models.")

    if 'video_agent' not in st.session_state:
        st.session_state['video_agent'] = VideoAgent()
    
    agent = st.session_state['video_agent']
    
    # Tabs
    tab_gen, tab_history = st.tabs(["✨ Generator", "📜 History"])
    
    with tab_gen:
        col_settings, col_preview = st.columns([1, 2])
        
        with col_settings:
            st.subheader("Configuration")
            
            # Provider Selection
            provider = st.selectbox(
                "AI Model Provider", 
                agent.manager.list_providers(),
                index=0,
                help="Select the underlying video generation model."
            )
            
            # Aspect Ratio
            aspect_ratio = st.selectbox(
                "Aspect Ratio",
                ["16:9 (Landscape)", "9:16 (Vertical/Shorts)", "1:1 (Square)"],
                index=0
            )
            
            # Style Presets
            style = st.selectbox(
                "Visual Style",
                ["Cinematic", "3D Animation", "Photorealistic", "Anime", "Vintage Film", "Cyberpunk"],
                index=0
            )
            
            # Advanced settings
            with st.expander("Advanced Settings"):
                negative_prompt = st.text_area("Negative Prompt", placeholder="low quality, blurry, distorted...")
                duration = st.slider("Duration (seconds)", 2, 10, 4)

        with col_preview:
            st.subheader("Prompt Engineering")
            
            prompt_input = st.text_area(
                "Describe your video idea",
                height=150,
                placeholder="A drone shot flying over a futuristic city at sunset, neon lights, 4k resolution..."
            )
            
            if st.button("🎥 Generate Video", type="primary", use_container_width=True):
                if not prompt_input:
                    st.warning("Please describe your video idea first.")
                else:
                    def start_gen():
                        result = agent.create_video(
                            context=prompt_input,
                            provider_name=provider,
                            style=style
                        )
                        job_data = result.get('job', {})
                        # Save to DB
                        save_video_job(
                            prompt=prompt_input,
                            optimized_prompt=result.get('optimized_prompt'),
                            provider=result.get('provider'),
                            status=job_data.get('status', 'pending'),
                            job_id=job_data.get('job_id'),
                            url=job_data.get('url')
                        )
                        return result

                    res = safe_action_wrapper(start_gen, "Director has initialized the render!")
                    if res:
                        st.session_state['last_video_job'] = res
                        st.rerun()

            # --- ACTIVE RENDER MONITOR ---
            if 'last_video_job' in st.session_state:
                job = st.session_state['last_video_job']
                job_data = job.get('job', {})
                jid = job_data.get('job_id')
                
                st.divider()
                st.markdown(f"**Current Task:** `{jid}`")
                
                # Polling / Status Logic Wrapper in Job Controls
                status_info = agent.manager.get_provider(job['provider']).get_status(jid)
                current_status = status_info.get('status')
                prog = status_info.get('progress', 0) if isinstance(status_info.get('progress'), (int, float)) else 0
                
                render_job_controls(
                    "Video Render", 
                    is_running=(current_status not in ['completed', 'failed']),
                    on_start=None, # Already started
                    on_stop=lambda: update_video_job_status(jid, 'stopped'),
                    progress=prog / 100.0,
                    status_text=f"🎥 Rendering ({current_status})... {prog}%"
                )
                
                if current_status == 'completed':
                    st.success("Render Complete!")
                    st.video(status_info.get('url'))
                    update_video_job_status(jid, 'completed', status_info.get('url'))
                    if st.button("Clear monitor"):
                        del st.session_state['last_video_job']
                        st.rerun()
                elif current_status == 'failed':
                    st.error(f"Render Failed: {status_info.get('error')}")
                    update_video_job_status(jid, 'failed')
                    if st.button("Retry Generation"):
                        del st.session_state['last_video_job']
                        st.rerun()

    with tab_history:
        st.subheader("🕵️ Video Archives")
        history = get_video_history()
        
        if not history:
            st.info("No videos generated yet. Launch your first cinematic render!")
        else:
            hist_df = pd.DataFrame(history)
            hist_df['created_at'] = pd.to_datetime(hist_df['created_at'], unit='s').dt.strftime('%m/%d %H:%M')
            
            # Use Enhanced Table for selection/bulk
            edited_hist = render_enhanced_table(hist_df[['id', 'provider', 'status', 'created_at', 'job_id']], key="video_hist_table")
            
            selected_ids = edited_hist[edited_hist['Select'] == True]['id'].tolist()
            if selected_ids:
                confirm_action("🗑️ Delete Selected", f"Permanently remove {len(selected_ids)} history items?", 
                               lambda: [get_connection().cursor().execute("DELETE FROM video_history WHERE id=?", (hid,)) for hid in selected_ids], 
                               key="bulk_del_vid")

            st.divider()
            
            # Detail Preview
            selected_job = st.selectbox("Select Video to Preview", hist_df['prompt'].str[:50].tolist())
            if selected_job:
                row = hist_df[hist_df['prompt'].str[:50] == selected_job].iloc[0]
                with st.container(border=True):
                    st.markdown(f"**Source Prompt:** {row['prompt']}")
                    st.markdown(f"**Optimized Prompt:** {row['optimized_prompt']}")
                    if row['url'] and row['status'] == 'completed':
                        st.video(row['url'])
                    else:
                        st.warning(f"Video unavailable. Status: {row['status']}")
