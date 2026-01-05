
import streamlit as st
import pandas as pd
from datetime import datetime
from database import get_connection, get_deals, get_tasks
from proxy_manager import proxy_manager

def get_db_metrics():
    """Fetch quick metrics for the dashboard."""
    try:
        conn = get_connection()
        # Leads
        leads = pd.read_sql_query("SELECT count(*) as count FROM leads", conn).iloc[0]['count']
        
        # Campaigns
        campaigns = pd.read_sql_query("SELECT count(*) as count FROM campaigns WHERE status='running'", conn).iloc[0]['count']
        
        conn.close()
        return leads, campaigns
    except:
        return 0, 0

def render_dashboard():
    # Header
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🚀 Mission Control")
        st.caption(f"System Status: ONLINE | {datetime.now().strftime('%A, %B %d, %I:%M %p')}")
    with col2:
        # Mini System Health
        status_color = "green" if proxy_manager.enabled else "orange"
        st.markdown(f"""
        <div style="text-align: right; padding: 10px; border: 1px solid #333; border-radius: 5px;">
            <b>Proxies:</b> :{status_color}[{'Active' if proxy_manager.enabled else 'Disabled'}]<br>
            <b>Automation:</b> {'Running' if st.session_state.get('automation_engine') and st.session_state['automation_engine'].is_running else 'Idle'}
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # --- High Level Metrics ---
    leads_count, active_campaigns = get_db_metrics()
    deals_val = sum(d['value'] for d in get_deals())
    tasks_count = len(get_tasks(status='pending'))
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Leads", leads_count, delta="Database")
    m2.metric("Pipeline Value", f"${deals_val:,.0f}", delta="Active Deals")
    m3.metric("Running Campaigns", active_campaigns, delta="Marketing")
    m4.metric("Pending Tasks", tasks_count, delta="Action Items")

    st.divider()

    # --- Navigation Grid ---
    st.subheader("📡 Operations Center")
    
    app_mode = st.session_state.get("app_mode", "B2B")
    
    if app_mode == "B2B":
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("#### 💼 Sales & CRM")
            st.info("Manage pipeline, leads, and tasks.")
            if st.button("Go to CRM", use_container_width=True):
                st.session_state['current_view'] = "CRM Dashboard"
                st.rerun()
            if st.button("View Pipeline", use_container_width=True):
                st.session_state['current_view'] = "Pipeline (Deals)"
                st.rerun()

        with c2:
            st.markdown("#### 📣 Marketing")
            st.info("Campaigns, Content, and Strategy.")
            if st.button("Manage Campaigns", use_container_width=True):
                st.session_state['current_view'] = "Campaigns"
                st.rerun()
            if st.button("Strategy Lab", use_container_width=True):
                st.session_state['current_view'] = "Strategy Laboratory"
                st.rerun()

        with c3:
            st.markdown("#### 🕵️ Lead Generation")
            st.info("Find new prospects and data.")
            if st.button("Lead Discovery", use_container_width=True):
                st.session_state['current_view'] = "Lead Discovery"
                st.rerun()
            if st.button("Mass Tools", use_container_width=True):
                st.session_state['current_view'] = "Mass Tools"
                st.rerun()

        st.markdown("") # Spacer
        
        c4, c5, c6 = st.columns(3)
        with c4:
            st.markdown("#### 📈 SEO & Growth")
            st.info("Audit sites and build backlinks.")
            if st.button("SEO Hub", use_container_width=True):
                st.session_state['current_view'] = "SEO Audit"
                st.rerun()

        with c5:
            st.markdown("#### 🤖 Automation & Agents")
            st.info("Configure agents and workflows.")
            if st.button("Automation Hub", use_container_width=True):
                st.session_state['current_view'] = "Automation Hub"
                st.rerun()
            if st.button("Agent Factory", use_container_width=True):
                st.session_state['current_view'] = "Agent Factory"
                st.rerun()

        with c6:
            st.markdown("#### ⚙️ System Admin")
            st.info("Settings and Configuration.")
            if st.button("Settings", use_container_width=True):
                st.session_state['current_view'] = "Settings"
                st.rerun()
                
    else:
        # B2C Layout (Simplified for now)
        st.info("B2C Dashboard Layout coming soon. Please use sidebar navigation.")
        if st.button("Go to Influencer Scout"):
            st.session_state['current_view'] = "Influencer Scout"
            st.rerun()
