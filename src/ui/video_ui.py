
import streamlit as st
import time
import pandas as pd
from datetime import datetime
from agents.video_agent import VideoAgent
from database import save_video_job, get_video_history, update_video_job_status, get_connection
from ui.components import (
    premium_header, safe_action_wrapper, render_job_controls, 
    render_enhanced_table, confirm_action
)

def render_video_studio():
    premium_header("🎬 Video Studio", "Generate, record, and edit cinematic content.")

    if 'video_agent' not in st.session_state:
        st.session_state['video_agent'] = VideoAgent()
    
    agent = st.session_state['video_agent']
    
    # Tabs
    tab_gen, tab_rec, tab_edit, tab_gallery = st.tabs(["✨ AI Generator", "🎥 Webcam Recorder", "✂️ Editor", "🎞️ Gallery"])
    
    # --- TAB 1: AI GENERATOR ---
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
            
            if st.button("🎥 Generate Video", type="primary", width="stretch"):
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

    # --- TAB 2: WEBCAM RECORDER ---
    with tab_rec:
        st.subheader("🎥 Direct Recording")
        st.caption("Record personalized intros for your outreach.")
        
        cam_video = st.camera_input("Record Video")
        
        if cam_video:
            st.video(cam_video)
            if st.button("💾 Save Recording", type="primary"):
                # Save bytes to disk/db
                ts = int(time.time())
                fname = f"rec_{ts}.mp4"
                with open(fname, "wb") as f:
                    f.write(cam_video.getbuffer())
                
                # Register in DB
                save_video_job(
                    prompt="Webcam Recording",
                    optimized_prompt="Personalized Video",
                    provider="Webcam",
                    status="completed",
                    job_id=f"webcam_{ts}",
                    url=fname # Local path for now
                )
                st.success(f"Saved to Video Library as {fname}!")

    # --- TAB 3: EDITOR ---
    with tab_edit:
        st.subheader("✂️ Sequence Editor")
        st.caption("Stitch clips together.")
        
        history = get_video_history()
        completed_videos = [v for v in history if v['status'] == 'completed']
        
        if completed_videos:
            # Multi-select clips
            selected_clips = st.multiselect(
                "Select Clips to Stitch (in order)", 
                options=completed_videos,
                format_func=lambda x: f"{x['id']}: {x['prompt'][:30]}...",
                key="editor_clips"
            )
            
            if selected_clips:
                st.write("### Sequence Preview")
                cols = st.columns(len(selected_clips))
                for i, clip in enumerate(selected_clips):
                    with cols[i]:
                        st.caption(f"{i+1}. {clip['prompt'][:10]}...")
                        # If local file vs URL
                        st.video(clip['url'])
                
                if st.button("Merge & Export", type="primary"):
                    st.toast("Rendering sequence (Simulation)...")
                    time.sleep(2)
                    st.success("Sequence exported! (Mock Integration)")
        else:
            st.info("No completed videos available to edit.")

    # --- TAB 4: GALLERY ---
    with tab_gallery:
        st.subheader("🎞️ Video Library")
        history = get_video_history()
        
        if not history:
            st.info("Library is empty.")
        else:
            # Filter bar
            filter_provider = st.selectbox("Filter by Provider", ["All"] + list(set(h['provider'] for h in history)), key="gal_filter")
            
            filtered = [h for h in history if filter_provider == "All" or h['provider'] == filter_provider]
            
            # Grid Layout
            search_q = st.text_input("🔍 Search Library", placeholder="Search prompts...")
            if search_q:
                filtered = [h for h in filtered if search_q.lower() in h['prompt'].lower()]

            cols = st.columns(3)
            for i, vid in enumerate(filtered):
                with cols[i % 3]:
                    with st.container(border=True):
                        st.caption(f"**{vid['prompt'][:40]}...**")
                        if vid['status'] == 'completed' and vid['url']:
                            st.video(vid['url'])
                        else:
                            st.info(f"Status: {vid['status']}")
                        
                        st.markdown(f"**ID:** `{vid['job_id']}`")
                        
                        bt_col1, bt_col2 = st.columns(2)
                        with bt_col1:
                             def delete_video_record(vid_id):
                                 conn = get_connection()
                                 conn.cursor().execute("DELETE FROM video_history WHERE id=?", (vid_id,))
                                 conn.commit()
                             
                             confirm_action("🗑️", "Delete?", lambda: delete_video_record(vid['id']), key=f"del_gal_{vid['id']}")
