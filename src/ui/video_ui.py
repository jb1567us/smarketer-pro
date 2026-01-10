import streamlit as st
import time
import asyncio
from agents.video_agent import VideoAgent

def render_video_studio():
    st.header("🎬 Smart Video Studio")
    st.caption("Generate cinematic AI videos using a fleet of browser-based engines.")

    if 'video_agent' not in st.session_state:
        st.session_state['video_agent'] = VideoAgent()
    
    agent = st.session_state['video_agent']
    
    # Tabs
    tab_gen, tab_auth, tab_history = st.tabs(["✨ Generator", "🔐 Auth Hub", "📜 History"])
    
    with tab_auth:
        st.subheader("Browser Session Manager")
        st.info("Log in to these services once to enable the Smart Router to use them.")
        
        providers = ["kling", "luma", "leonardo"]
        cols = st.columns(3)
        for i, p_name in enumerate(providers):
            p = agent.manager.get_provider(p_name)
            if not p or p_name == "mock": continue
            
            with cols[i]:
                st.markdown(f"### {p_name.title()}")
                st.caption(f"Daily Limit: {p.daily_limit}")
                st.caption(f"Tags: {', '.join(p.capabilities)}")
                
                if st.button(f"🔑 Login to {p_name.title()}", key=f"login_{p_name}"):
                    # Async button handler
                    with st.spinner(f"Launching {p_name} login window... Check your taskbar!"):
                        asyncio.run(p.login_interactive())
                    st.success("Session saved!")
                    
                # [NEW] Create Account Button
                from video_gen.auth_configs import VIDEO_AUTH_CONFIGS
                if p_name in VIDEO_AUTH_CONFIGS:
                    if st.button(f"🆕 Register {p_name.title()}", key=f"reg_{p_name}"):
                        st.info("Starting Auto-Registration Agent...")
                        
                        # Initialize Agent
                        from agents.account_creator import AccountCreatorAgent
                        from config import get_cpanel_config
                        from proxy_manager import proxy_manager
                        
                        cp_conf = get_cpanel_config()
                        if not cp_conf or not cp_conf.get('url'):
                            st.error("cPanel not configured!")
                        else:
                            creator_agent = AccountCreatorAgent(cp_conf)
                            
                            # Proxy logic
                            proxy = proxy_manager.get_proxy()
                            if not proxy: 
                                # Optimization: Use ensure_fresh_proxies instead of forcing a full harvest
                                # honor the 24h freshness pull the user mentioned
                                asyncio.run(proxy_manager.ensure_fresh_proxies())
                                proxy = proxy_manager.get_proxy()
                            
                            st.write(f"Using Proxy: {proxy}")
                            
                            # Run
                            reg_url = VIDEO_AUTH_CONFIGS[p_name]['registration_url']
                            
                            with st.status(f"Creating {p_name} account...", expanded=True):
                                async def run_creation():
                                    return await creator_agent.create_account(
                                        p_name,
                                        reg_url,
                                        account_details={},
                                        proxy=proxy
                                    )
                                try:
                                    res = asyncio.run(run_creation())
                                    st.write(res)
                                    if "verified" in str(res).lower():
                                        st.success("Account Created! You can now Login.")
                                    else:
                                        st.warning("Check results above.")
                                except Exception as e:
                                    st.error(f"Failed: {e}")
                
                # Manual Macro Recording Button
                if st.button(f"🔴 Record Macro for {p_name.title()}", key=f"rec_manual_{p_name}"):
                    from database import save_registration_macro
                    from utils.browser_manager import BrowserManager
                    
                    async def record_macro_direct(platform, url):
                        bm = BrowserManager(session_id=f"record_{platform}")
                        await bm.launch(headless=False)
                        await bm.page.goto(url)
                        await bm.start_recording()
                        st.info("🔴 **RECORDING ACTIVE**")
                        st.write(f"Recording actions for {platform}. Close the window when done.")
                        
                        while True:
                            await asyncio.sleep(0.5)
                            if bm.page.is_closed(): break
                            
                        events = await bm.stop_recording()
                        if events:
                            save_registration_macro(platform, events)
                            st.success(f"Macro saved for {platform}!")
                        await bm.close()
                    
                    asyncio.run(record_macro_direct(p_name, VIDEO_AUTH_CONFIGS.get(p_name, {}).get('registration_url', 'https://google.com')))
                    st.rerun()

        st.divider()
        st.subheader("⚠️ Pending Registration Tasks")
        from database import get_registration_tasks, delete_registration_task, save_registration_macro, mark_registration_task_completed
        from utils.browser_manager import BrowserManager
        import json

        v_tasks = get_registration_tasks(status='pending')
        # Only show tasks related to video providers if we want, or show all. 
        # User probably wants to see relevant ones here.
        video_providers = ["kling", "luma", "leonardo", "runway"]
        v_tasks = [t for t in v_tasks if t['platform'].lower() in video_providers]

        if v_tasks:
            for task in v_tasks:
                with st.expander(f"Task: {task['platform']} - {task['url']}", expanded=True):
                    col_t1, col_t2 = st.columns([3, 1])
                    with col_t1:
                        st.write(f"**URL:** {task['url']}")
                        try:
                            d = json.loads(task['details'])
                            if 'error' in d: st.error(f"Error: {d['error']}")
                        except: pass
                    with col_t2:
                        if st.button("🔴 Record", key=f"rec_v_{task['id']}"):
                            async def rec_flow():
                                bm = BrowserManager(session_id=f"record_{task['platform']}")
                                await bm.launch(headless=False)
                                await bm.page.goto(task['url'])
                                await bm.start_recording()
                                st.info("🔴 **RECORDING active**")
                                while True:
                                    await asyncio.sleep(0.5)
                                    if bm.page.is_closed(): break
                                events = await bm.stop_recording()
                                if events:
                                    save_registration_macro(task['platform'], events)
                                    mark_registration_task_completed(task['id'])
                            asyncio.run(rec_flow())
                            st.rerun()
                        if st.button("🗑️", key=f"del_v_{task['id']}"):
                            delete_registration_task(task['id'])
                            st.rerun()
        else:
            st.info("No pending video registration tasks.")

    with tab_gen:
        col_settings, col_preview = st.columns([1, 2])
        
        with col_settings:
            st.subheader("Configuration")
            
            # Provider Selection
            provider_list = agent.manager.list_providers()
            # Ensure 'smart' is default
            idx = 0
            if "smart" in provider_list:
                idx = provider_list.index("smart")

            provider_selection = st.selectbox(
                "Engine Selection", 
                provider_list,
                index=idx,
                help="Select 'smart' to auto-route based on prompt style and daily limits."
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
                duration = st.slider("Duration (seconds)", 2, 10, 5)

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
                    with st.spinner("🤖 Smart Router is selecting the best engine..."):
                         # 1. Route Request
                        selected_provider = agent.manager.smart_route(prompt_input, style, provider_selection)
                        st.info(f"Routing task to: **{selected_provider.name.upper()}** (Best match for '{style}')")
                        
                        # 2. Execute
                        try:
                            # Direct call to provider for now to bypass agent 'discuss' wrapper if needed, 
                            # or update agent to support smart routing.
                            # For MVP simplicity, we call the provider directly here since the logic is complex async
                            
                            # Log usage
                            agent.manager.log_usage(selected_provider.name)
                            
                            result = asyncio.run(selected_provider.generate_video(
                                prompt=prompt_input,
                                style=style,
                                negative_prompt=negative_prompt
                            ))
                            
                            if result.get('status') == 'failed':
                                st.error(f"Generation Failed: {result.get('error')}")
                            else:
                                st.success("Generation Started!")
                                # Store result
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
                
                st.divider()
                st.markdown(f"**Job ID:** `{job.get('job_id')}` | **Provider:** `{job.get('provider')}`")
                
                # Polling/Display Logic
                status_container = st.empty()
                video_container = st.empty()
                
                status = job.get('status')
                
                if status == 'completed':
                    status_container.success("Complete!")
                    if job.get('url'):
                        video_container.video(job.get('url'))
                elif status == 'failed':
                    status_container.error(f"Failed: {job.get('error')}")
                else: 
                     # Simple immediate check for MVP (since Kling mock returns success)
                    try:
                        provider_inst = agent.manager.get_provider(job.get('provider'))
                        current_status = asyncio.run(provider_inst.get_status(job.get('job_id')))
                        
                        if current_status.get('status') == 'completed':
                            status_container.success("Render Complete!")
                            video_container.video(current_status.get('url'))
                            # Update history
                            job['status'] = 'completed'
                            job['url'] = current_status.get('url')
                        else:
                            status_container.info(f"Status: {current_status.get('status')}...")
                    except Exception as e:
                        status_container.error(f"Poll Error: {e}")

    with tab_history:
        st.subheader("Generation History")
        if 'video_history' in st.session_state and st.session_state['video_history']:
            for item in st.session_state['video_history']:
                with st.expander(f"[{item.get('provider').upper()}] {item.get('optimized_prompt')[:50]}...", expanded=False):
                    if item.get('url'): # Check locally cached/updated URL
                        st.video(item.get('url'))
                    # Also try to check if the 'job' sub-dict has it (from old structure)
                    elif item.get('job', {}).get('url'):
                        st.video(item['job']['url'])
                    else:
                        st.warning("Processing or Failed.")
        else:
            st.info("No videos generated yet.")
