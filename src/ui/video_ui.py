import streamlit as st
import time
from agents.video_agent import VideoAgent

def render_video_studio():
    st.header("🎬 Video Studio")
    st.caption("Generate cinematic AI videos for your campaigns using state-of-the-art models.")

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
                    with st.spinner("🎬 Director (Agent) is crafting the prompt and initializing render..."):
                        # call agent
                        try:
                            result = agent.create_video(
                                context=prompt_input,
                                provider_name=provider,
                                style=style
                            )
                            
                            st.success("Generation Started!")
                            
                            # Store result in session state to display below
                            st.session_state['last_video_job'] = result
                            
                            # Add to history
                            if 'video_history' not in st.session_state:
                                st.session_state['video_history'] = []
                            st.session_state['video_history'].insert(0, result)
                            
                        except Exception as e:
                            st.error(f"Generation failed: {str(e)}")

            # Result Display
            if 'last_video_job' in st.session_state:
                job = st.session_state['last_video_job']
                job_data = job.get('job', {})
                
                st.divider()
                st.markdown(f"**Job ID:** `{job_data.get('job_id')}` | **Provider:** `{job.get('provider')}`")
                st.markdown(f"**Optimized Prompt:**")
                st.info(job.get('optimized_prompt'))
                
                # Polling/Display Logic
                status_container = st.empty()
                video_container = st.empty()
                
                status = job_data.get('status')
                
                # Initial render
                if status == 'completed':
                    status_container.success("Complete!")
                    if job_data.get('url'):
                        video_container.video(job_data.get('url'))
                elif status == 'failed':
                    status_container.error(f"Failed: {job_data.get('error')}")
                else:
                    # Poll loop if it's a fresh job or mock
                    # In a real app, this might be better handled with a "Check Status" button or background loop
                    # For this mock/demo, we'll do a short loop
                    progress_bar = status_container.progress(0, text=f"Processing ({status})...")
                    
                    for _ in range(20): # Poll for up to 20 seconds
                        time.sleep(1)
                        # Re-fetch status
                        current_status = agent.manager.get_provider(job['provider']).get_status(job_data['job_id'])
                        
                        s_txt = current_status.get('status')
                        prog = current_status.get('progress', 0)
                        
                        if s_txt == 'completed':
                            progress_bar.empty()
                            status_container.success("Render Complete!")
                            video_container.video(current_status.get('url'))
                            # Update the history item
                            job_data['status'] = 'completed'
                            job_data['url'] = current_status.get('url')
                            break
                        elif s_txt == 'failed':
                            progress_bar.empty()
                            status_container.error("Render Failed.")
                            break
                        else:
                            progress_bar.progress(prog, text=f"Rendering ({s_txt})... {prog}%")

    with tab_history:
        st.subheader("Generation History")
        if 'video_history' in st.session_state and st.session_state['video_history']:
            for item in st.session_state['video_history']:
                with st.expander(f"{item.get('optimized_prompt')[:60]}...", expanded=False):
                    st.text(f"Provider: {item.get('provider')}")
                    j = item.get('job', {})
                    if j.get('url'):
                        st.video(j.get('url'))
                    else:
                        st.warning("Video URL not available (expired or failed).")
        else:
            st.info("No videos generated yet.")
