import streamlit as st
import pandas as pd
import time
import asyncio
import json
from datetime import datetime, time
from database import (
    get_scheduled_posts, delete_scheduled_post, save_scheduled_post, load_data, add_lead,
    save_creative_content
)
from agents import SocialMediaAgent, SocialListeningAgent
from ui.components import render_enhanced_table, render_data_management_bar, render_page_chat

def render_social_scheduler_page():
    st.header("📅 Social Media Hub")
    st.caption("Plan and schedule your social media presence.")
    
    tab1, tab2, tab3 = st.tabs(["📋 Scheduled Posts", "💡 Strategy Generator", "🔗 Linked Accounts"])
    with tab1:
        st.subheader("Upcoming Content")
        scheduled = get_scheduled_posts(status='pending')
        
        if not scheduled:
            st.info("No posts scheduled yet. Use the 'New Post' section below.")
        else:
            # 1. Standard Data Management Bar
            render_data_management_bar(scheduled, filename_prefix="social_posts")

            # 2. Enhanced Table
            sched_df = pd.DataFrame(scheduled)
            edited_sched = render_enhanced_table(sched_df[['id', 'agent_type', 'platforms', 'content', 'scheduled_at']], key="social_sched_table")
            
            selected_posts = edited_sched[edited_sched['Select'] == True]
            if not selected_posts.empty:
                if st.button(f"🗑️ Delete {len(selected_posts)} Selected Posts", type="secondary"):
                    for pid in selected_posts['id'].tolist():
                        delete_scheduled_post(pid)
                    st.success("Deleted!")
                    st.rerun()

            st.divider()
            st.subheader("🖼️ Detail View")
            for p in scheduled:
                with st.expander(f"📌 {p['agent_type']}: {p['content'][:50]}...", expanded=False):
                    st.write(p['content'])
                    platforms = json.loads(p['platforms'])
                    st.caption(f"📱 Platforms: {', '.join(platforms)} | 📅 {pd.to_datetime(p['scheduled_at'], unit='s').strftime('%Y-%m-%d %H:%M')}")
                    if st.button("🗑️ Delete Post", key=f"del_post_single_{p['id']}"):
                        delete_scheduled_post(p['id'])
                        st.rerun()

        # 3. Page Level Chat
        render_page_chat(
            "Social Strategy", 
            SocialMediaAgent(), 
            json.dumps(scheduled, indent=2)
        )
        st.divider()
        st.subheader("➕ Create New Post")
        with st.form("social_post"):
            platforms = st.multiselect("Platforms", ["LinkedIn", "X (Twitter)", "Instagram", "TikTok", "Facebook"], default=["LinkedIn"])
            content = st.text_area("Post Content", height=150, placeholder="Write your post here or use an agent result...")
            
            col1, col2 = st.columns(2)
            with col1:
                d_date = st.date_input("Schedule Date", value=datetime.now())
            with col2:
                d_time = st.time_input("Schedule Time", value=datetime.now().time())
            
            if st.form_submit_button("Schedule Post", use_container_width=True):
                if content and platforms:
                    # Combine date and time
                    dt = datetime.combine(d_date, d_time)
                    ts = int(dt.timestamp())
                    save_scheduled_post("Manual", platforms, content, ts)
                    st.success("Post scheduled successfully!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Please provide both content and at least one platform.")
    with tab2:
        st.subheader("Platform Strategies")
        p_niche = st.text_input("Niche", key="soc_niche", placeholder="e.g. SaaS Founders")
        p_prod = st.text_input("Product/Service", key="soc_prod", placeholder="e.g. B2B Outreach Tool")
        strat_platform = st.selectbox("Select Platform", ["TikTok", "Instagram", "LinkedIn"])
        
        if st.button("Generate Strategy", type="primary"):
            agent = SocialMediaAgent()
            with st.spinner(f"Architecting {strat_platform} strategy..."):
                if strat_platform == "TikTok":
                    res = agent.generate_tiktok_strategy(p_niche, p_prod)
                elif strat_platform == "Instagram":
                    res = agent.generate_instagram_strategy(p_niche, p_prod)
                else:
                    res = agent.think(f"Generate strategy for {strat_platform} in {p_niche} for {p_prod}")
                
                st.session_state['last_social_strategy'] = res
                st.rerun()
        
        if 'last_social_strategy' in st.session_state:
            st.divider()
            st.json(st.session_state['last_social_strategy'])
            # Allow creating a post from strategy
            if st.button("Convert to Post Draft"):
                # Extract some content if possible
                res = st.session_state['last_social_strategy']
                content_draft = ""
                if isinstance(res, dict):
                     # Try to find common keys
                     content_draft = res.get('hook', '') or res.get('script', '') or str(res)
                else:
                     content_draft = str(res)
                
                st.session_state['current_view'] = "Social Scheduler"
                # We can't easily populate the form cross-tab/view without more state
                st.info("Draft ready (Simulated). Copy-paste the content above into the Scheduler tab.")
    with tab3:
        st.subheader("Linked Accounts")
        accounts = [
            {"name": "LinkedIn", "status": "Connected", "user": "Baron (Pro)"},
            {"name": "X (Twitter)", "status": "Connected", "user": "@SmarketerAI"},
            {"name": "Instagram", "status": "Connected", "user": "smarketer_official"},
            {"name": "TikTok", "status": "Disconnected", "user": "N/A"},
            {"name": "Facebook", "status": "Disconnected", "user": "N/A"}
        ]
        
        for acc in accounts:
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.markdown(f"**{acc['name']}**")
            with col2:
                color = "green" if acc['status'] == "Connected" else "gray"
                st.markdown(f":{color}[{acc['status']}] ({acc['user']})")
            with col3:
                if acc['status'] == "Connected":
                    st.button("Disconnect", key=f"dc_{acc['name']}")
                else:
                    st.button("Connect", key=f"cn_{acc['name']}", type="primary")


def render_social_pulse_page():
    st.header("📡 Social Listening Pulse")
    st.caption("Monitor real-time buying signals and competitor mentions across the web.")
    
    # Keyword Configuration
    with st.expander("⚙️ Listening Configuration", expanded=True):
        # Presets
        st.markdown("**Quick Start Presets:**")
        col_p1, col_p2, col_p3 = st.columns(3)
        
        preset_val = None
        if col_p1.button("🔥 Buying Signals"):
            preset_val = "looking for a [niche] tool, recommend a [niche] agency, best alternative to [competitor] -site:[competitor].com"
        if col_p2.button("😡 Competitor Complaints"):
            preset_val = "[competitor] too expensive, [competitor] downtime, hate [competitor], [competitor] support sucks -site:[competitor].com"
        if col_p3.button("📣 Brand Mentions"):
            preset_val = "Smarketer Pro -from:SmarketerPro, @SmarketerAI -from:SmarketerAI"
            
        # Update the ACTUAL key used by the text input
        if preset_val:
            st.session_state['sl_kw_input_final'] = preset_val
            st.rerun()
        # Initialize default if not present
        if 'sl_kw_input_final' not in st.session_state:
            st.session_state['sl_kw_input_final'] = "SEO services, marketing automation, b2b leads"
        sl_keywords = st.text_input(
            "Keywords to Monitor (comma separated)", 
            key='sl_kw_input_final'
        )
        
        col_run, col_sets = st.columns([1, 2])
        with col_sets:
            scan_depth = st.slider("Scan Depth (Results per Platform)", 5, 20, 5)
        
        with col_run:
            if st.button("🚀 Scan Now", type="primary"):
                st.session_state['sl_kw_input'] = sl_keywords # persist
                agent = SocialListeningAgent()
                with st.spinner("Listening to the social web..."):
                    # Split and run
                    kws = [k.strip() for k in sl_keywords.split(",")]
                    signals = asyncio.run(agent.listen_for_keywords(kws, num_results=scan_depth))
                    st.session_state['social_signals'] = signals
                    st.rerun()
    # Feed Display
    if 'social_signals' in st.session_state:
        signals = st.session_state['social_signals']
        
        # Filters
        col_f1, col_f2 = st.columns([3, 1])
        with col_f1:
            st.subheader(f"Live Feed ({len(signals)} Signals)")
        if high_intent_only:
            signals = [s for s in signals if s.get('analysis', {}).get('intent_score', 0) >= 7]
            if not signals:
                st.info("No high intent signals found in this batch.")
        
        # 1. Standard Data Management Bar
        render_data_management_bar(signals, filename_prefix="social_pulse")

        # 2. Enhanced Table
        pulse_df = pd.DataFrame([
            {
                "id": idx,
                "Platform": s['platform'],
                "User": s['user'],
                "Content": s['content'][:100],
                "Intent": s.get('analysis', {}).get('intent_score', 0)
            } for idx, s in enumerate(signals)
        ])
        render_enhanced_table(pulse_df, key="social_pulse_table")

        # 3. Page Level Chat
        render_page_chat(
            "Social Pulse Analysis", 
            SocialListeningAgent(), 
            json.dumps(signals, indent=2)
        )
        
        st.divider()
        
        # Anti-Hallucination Check
        if len(signals) == 1 and signals[0].get('content') == "NO_DATA_FOUND":
            st.warning("⚠️ No signals found. SearXNG might be warming up or no recent matches.")
            st.info("💡 Try a broader keyword or check if Docker is running.")
        else:
            for idx, item in enumerate(signals):
                analysis = item.get('analysis', {})
                intent_score = analysis.get('intent_score', 0)
                classification = analysis.get('classification', 'General')
                
                # Color code based on intent
                # Intent Score Bar
                score_color = "red" if intent_score >= 8 else "orange" if intent_score >= 5 else "green" # High intent = Red hot? Or Green? Usually sales is Green/Red. Let's use Red for HOT.
                
                with st.container(border=True):
                    c1, c2 = st.columns([0.1, 4])
                    with c1:
                        # Icon based on platform
                        pmap = {"twitter": "🐦", "linkedin": "💼", "reddit": "🤖"}
                        st.write(pmap.get(item['platform'], "🌐"))
                    
                    with c2:
                        # Header: User + Score Badge
                        col_h1, col_h2 = st.columns([3, 1])
                        with col_h1:
                            st.markdown(f"**{item['user']}** • {item['timestamp']}")
                        with col_h2:
                            if intent_score >= 8:
                                st.markdown(f":fire: **{intent_score}/10**")
                            else:
                                st.markdown(f"**{intent_score}/10**")
                        
                        st.markdown(f"*{item['content']}*")
                        
                        # AI Insights
                        st.markdown(f"**AI:** :blue[{classification}]")
                        st.progress(intent_score / 10.0, text=f"Buying Intent: {intent_score}/10")
                        
                        st.caption(f"💡 Strategy: {analysis.get('suggested_reply_angle')}")
                        
                        # Actions
                        ac1, ac2 = st.columns(2)
                        with ac1:
                            if st.button("Draft Reply", key=f"repl_{idx}"):
                                agent = SocialListeningAgent()
                                draft = agent.generate_reply(item['content'], analysis.get('suggested_reply_angle'))
                                st.session_state[f'draft_{idx}'] = draft
                        with ac2:
                            if st.button("Save as Lead", key=f"lead_{idx}"):
                                from database import add_lead
                                add_lead(item['url'], f"{item['user']}@social.com", source="Social Pulse", company_name=item['platform'])
                                st.toast("Lead saved to CRM!")
                        
                        if f'draft_{idx}' in st.session_state:
                            st.text_area("Draft", value=st.session_state[f'draft_{idx}'], key=f"txt_{idx}")
                            if st.button("Copy to Clipboard (Sim)", key=f"copy_{idx}"):
                                st.toast("Copied to clipboard!")
