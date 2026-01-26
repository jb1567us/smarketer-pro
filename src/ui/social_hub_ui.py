
import streamlit as st
import pandas as pd
import time
import asyncio
import json
import calendar
from datetime import datetime, timedelta
from database import (
    get_scheduled_posts, delete_scheduled_post, save_scheduled_post, update_scheduled_post, 
    add_lead, get_platform_credentials, save_platform_credential, delete_platform_credential
)
from agents import CopywriterAgent, SocialListeningAgent
from ui.components import (
    render_enhanced_table, render_data_management_bar, render_page_chat,
    premium_header, safe_action_wrapper, confirm_action
)

def render_social_scheduler_page():
    premium_header("📅 Social Media Hub", "Plan, visualizations, and schedule your social media presence.")
    
    # Tabs
    tab_cal, tab_create, tab_settings = st.tabs(["🗓️ Calendar & Queue", "✨ Create & Strategy", "🔗 Accounts"])
    
    # --- TAB 1: CALENDAR & QUEUE ---
    with tab_cal:
        st.subheader("Content Calendar")
        
        # Fetch Posts
        scheduled = get_scheduled_posts(status='pending')
        
        # Calendar Visualization (Simple Grid)
        # Select Month
        c_col1, c_col2 = st.columns([1, 4])
        with c_col1:
            view_date = st.date_input("View Month", value=datetime.now(), key="cal_view_date")
        
        year, month = view_date.year, view_date.month
        cal = calendar.monthcalendar(year, month)
        
        # Render Calendar Grid
        cols = st.columns(7)
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, d in enumerate(days):
            cols[i].markdown(f"**{d}**", help="Day of Week")
            
        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                with cols[i]:
                    if day == 0:
                        st.markdown("")
                    else:
                        # Find posts for this day
                        day_posts = []
                        current_dt_start = datetime(year, month, day).timestamp()
                        current_dt_end = current_dt_start + 86400
                        
                        for p in scheduled:
                            if current_dt_start <= p['scheduled_at'] < current_dt_end:
                                day_posts.append(p)
                        
                        # Render Cell
                        bg_color = "rgba(76, 175, 80, 0.2)" if day_posts else "rgba(128,128,128,0.1)"
                        border = "2px solid #4CAF50" if datetime.now().day == day and datetime.now().month == month else "1px solid #444"
                        
                        box_html = f"""
                        <div style="
                            border: {border}; 
                            border-radius: 5px; 
                            background-color: {bg_color}; 
                            padding: 5px; 
                            height: 100px; 
                            font-size: 0.8em;
                            overflow-y: auto;">
                            <div style="font-weight: bold; margin-bottom: 3px;">{day}</div>
                        """
                        for dp in day_posts:
                             box_html += f"<div style='background: #333; margin-bottom: 2px; padding: 2px; border-radius: 3px; font-size: 0.7em;' title='{dp['content']}'>{dp['platforms']}</div>"
                        
                        box_html += "</div>"
                        st.markdown(box_html, unsafe_allow_html=True)

        st.divider()
        st.subheader("Manage Queue")

        if not scheduled:
            st.info("No posts scheduled. Go to 'Create & Strategy' to add content.")
        else:
            sched_df = pd.DataFrame(scheduled)
            # Format Check
            if 'platforms' in sched_df.columns:
                 sched_df['platforms'] = sched_df['platforms'].astype(str)
            
            # Date Filter
            d_col1, d_col2 = st.columns([1, 4])
            with d_col1:
                q_days = st.number_input("Filter Days Ahead", value=30, min_value=1)
                
            cutoff = datetime.now().timestamp() + (q_days * 86400)
            sched_df = sched_df[sched_df['scheduled_at'] <= cutoff]

            edited_sched = render_enhanced_table(
                sched_df[['id', 'agent_type', 'platforms', 'content', 'scheduled_at']], 
                key="social_sched_table"
            )
            
            selected_ids = edited_sched[edited_sched['Select'] == True]['id'].tolist() if 'Select' in edited_sched.columns else []
            if selected_ids:
                confirm_action(f"🗑️ Bulk Delete", f"Delete {len(selected_ids)} scheduled posts?", 
                               lambda: [delete_scheduled_post(pid) for pid in selected_ids], key="bulk_del_social")
                               
    # --- TAB 2: CREATE & STRATEGY ---
    with tab_create:
        c_1, c_2 = st.columns([3, 2])
        
        with c_1:
            st.subheader("📝 New Post")
            with st.form("social_post_form"):
                 platforms = st.multiselect("Platforms", ["LinkedIn", "X (Twitter)", "Instagram", "Facebook"], default=["LinkedIn"])
                 
                 draft_content = st.session_state.get('social_draft_content', "")
                 content = st.text_area("Content", value=draft_content, height=200)
                 
                 d_col1, d_col2 = st.columns(2)
                 with d_col1:
                     s_date = st.date_input("Date", value=datetime.now())
                 with d_col2:
                     s_time = st.time_input("Time", value=(datetime.now() + timedelta(hours=1)).time())
                     
                 submitted = st.form_submit_button("📅 Schedule Post", type="primary", width="stretch")
                 if submitted:
                     if content and platforms:
                         try:
                             dt = datetime.combine(s_date, s_time)
                             ts = int(dt.timestamp())
                             save_scheduled_post("Manual", json.dumps(platforms), content, ts)
                             st.success(f"Post scheduled for {dt}!")
                             st.session_state.pop('social_draft_content', None)
                             time.sleep(1)
                             st.rerun()
                         except Exception as e:
                             st.error(f"Failed to schedule: {e}")
                     else:
                         st.error("Content and Platform required.")
        
        with c_2:
            st.subheader("💡 AI Strategy")
            st.caption("Generate ideas or optimize content.")
            
            mode = st.radio("Mode", ["Ideation", "Optimization"], horizontal=True)
            
            if mode == "Ideation":
                niche = st.text_input("Target Audience / Niche", placeholder="e.g. SaaS Founders")
                topic = st.text_input("Topic", placeholder="e.g. AI Automation")
                
                if st.button("Generate Ideas"):
                    agent = CopywriterAgent()
                    with st.spinner("Brainstorming..."):
                        ideas = agent.run(f"Generate 5 viral social media post ideas for {niche} about {topic}. Format as a list.")
                        st.session_state['social_ideas'] = ideas
                
                if 'social_ideas' in st.session_state:
                    st.info(st.session_state['social_ideas'])
                    if st.button("Use Ideas"):
                        st.session_state['social_draft_content'] = st.session_state['social_ideas']
            
            elif mode == "Optimization":
                 current_draft = st.session_state.get('social_draft_content', "")
                 st.caption("Optimizes the content in the 'New Post' content box.")
                 if st.button("Refine Draft", disabled=not current_draft):
                      agent = CopywriterAgent()
                      with st.spinner("Polishing..."):
                          better = agent.run(f"Rewrite this for maximum engagement on LinkedIn/Twitter: '{current_draft}'")
                          st.session_state['social_draft_content'] = better
                          st.rerun()

    # --- TAB 3: ACCOUNTS ---
    with tab_settings:
        st.subheader("Linked Social Accounts")
        st.caption("Manage credentials for auto-posting.")
        
        platforms_list = ["LinkedIn", "X (Twitter)", "Instagram", "Facebook"]
        
        cols = st.columns(2)
        for i, plat in enumerate(platforms_list):
            with cols[i % 2]:
                with st.container(border=True):
                    st.markdown(f"### {plat}")
                    creds = get_platform_credentials(plat)
                    
                    if creds:
                        st.success(f"✅ Connected as {creds.get('username', 'Unknown')}")
                        if st.button(f"Disconnect {plat}", key=f"dc_{plat}"):
                            delete_platform_credential(plat)
                            st.rerun()
                    else:
                        st.warning("❌ Not Connected")
                        with st.popover(f"Connect {plat}"):
                            u = st.text_input(f"Username/Email", key=f"u_{plat}")
                            p = st.text_input(f"Password/API Key", type="password", key=f"p_{plat}")
                            if st.button(f"Save Credentials", key=f"sv_{plat}"):
                                try:
                                    save_platform_credential(plat, username=u, api_key=p)
                                    st.success("Saved!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Save failed: {e}")

def render_social_pulse_page():
    premium_header("📡 Social Listening Pulse", "Monitor real-time buying signals and competitor mentions.")

    # ... (Keep existing Logic but simplified/cleaned)
    if 'sl_keywords' not in st.session_state: st.session_state['sl_keywords'] = "SEO, Marketing, AI Agents"
    
    kws = st.text_input("Keywords (comma separated)", value=st.session_state['sl_keywords'])
    st.session_state['sl_keywords'] = kws
    
    if st.button("🚀 Scan Now", type="primary"):
        agent = SocialListeningAgent()
        with st.spinner("Scanning social web..."):
            kw_list = [k.strip() for k in kws.split(',')]
            signals = asyncio.run(agent.listen_for_keywords(kw_list, num_results=5))
            st.session_state['social_signals'] = signals
            st.rerun()
            
    if 'social_signals' in st.session_state:
        signals = st.session_state['social_signals']
        st.divider()
        st.subheader(f"Live Feed ({len(signals)})")
        
        for i, s in enumerate(signals):
            with st.container(border=True):
                c1, c2 = st.columns([1, 4])
                with c1:
                    st.markdown(f"**{s.get('platform', 'Web')}**")
                    st.caption(s.get('user', 'Anon'))
                with c2:
                    st.markdown(s.get('content', ''))
                    score = s.get('analysis', {}).get('intent_score', 0)
                    st.progress(score/10, text=f"Intent Score: {score}/10")
                    
                    if st.button("Save as Lead", key=f"sl_lead_{i}"):
                        try:
                            add_lead(s.get('url', 'social'), f"{s.get('user')}@social.tmp", source=f"Social Pulse: {s.get('platform')}", company_name=s.get('platform'))
                            st.toast("Lead Saved!")
                        except Exception as e:
                            st.error(f"Failed to save lead: {e}")
