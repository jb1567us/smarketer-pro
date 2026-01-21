from database import get_connection, get_deals, get_tasks
from proxy_manager import proxy_manager
from datetime import datetime
import streamlit as st
from ui.components import premium_header, safe_action_wrapper

def get_db_metrics():
    """Fetch quick metrics for the dashboard with safety wrapping."""
    def _fetch():
        conn = get_connection()
        leads = pd.read_sql_query("SELECT count(*) as count FROM leads", conn).iloc[0]['count']
        campaigns = pd.read_sql_query("SELECT count(*) as count FROM campaigns WHERE status='running'", conn).iloc[0]['count']
        conn.close()
        return leads, campaigns
    
    metrics = safe_action_wrapper(_fetch, success_message=None)
    return metrics if metrics else (0, 0)

def render_dashboard():
    premium_header("🚀 Mission Control", f"System Status: ONLINE | {datetime.now().strftime('%A, %B %d, %I:%M %p')}")
    
    # --- Sidebar Filters ---
    st.sidebar.markdown("### 📅 Global Filters")
    date_filter = st.sidebar.date_input("Date Range", [datetime(2026, 1, 1), datetime.now()])
    
    col1, col2 = st.columns([3, 1])
    with col2:
        # Mini System Health
        status_color = "green" if proxy_manager.enabled else "orange"
        engine = st.session_state.get('automation_engine')
        is_running = engine and getattr(engine, 'is_running', False)
        
        # Auto-refresh logic (Non-blocking improvement)
        if is_running:
            refresh = st.checkbox("Auto-refresh (30s)", value=False, key="dash_refresh")
            if refresh:
                # Instead of sleep(2), we only rerun if a significant interval has passed
                # This is still a bit 'Streamlit-style' but less intrusive than 2 seconds sleep
                last_refresh = st.session_state.get('last_dash_refresh', 0)
                if time.time() - last_refresh > 30:
                    st.session_state['last_dash_refresh'] = time.time()
                    st.rerun()
        
        if st.button("🔄 Refresh Data", width="stretch"):
            st.rerun()

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

    # --- Quickstart Guide (New User Onboarding) ---
    st.markdown("### 🚀 Quickstart Guide")
    with st.expander("Show Setup Checklist", expanded=not active_campaigns):
        st.markdown("""
        Follow this "Happy Path" to get your first outreach campaign running:
        
        1. **Connect Email**: Go to **Settings** and configure your sending account.
        2. **Find Leads**: Go to **Lead Discovery** or Import CSV to build your prospect list.
        3. **Create Campaign**: Go to **Campaigns** and start a new Nurture Campaign.
        4. **Launch**: Review your email sequence and click "Launch" in the campaign workspace.
        """)
        
        c1, c2, c3, c4 = st.columns(4)
        if c1.button("1. Connect Email"):
            st.session_state['current_view'] = "Settings"
            st.rerun()
        if c2.button("2. Find Leads"):
            st.session_state['current_view'] = "Lead Discovery"
            st.rerun()
        if c3.button("3. New Campaign"):
            st.session_state['current_view'] = "Campaigns"
            st.rerun()
        if c4.button("4. Launch"):
            st.session_state['current_view'] = "Campaigns"
            st.rerun()

    # --- Navigation Grid ---
    st.subheader("📡 Operations Center")
    
    app_mode = st.session_state.get("app_mode", "B2B")
    
    # Custom CSS for interactive cards
    st.markdown("""
        <style>
        .nav-card {
            background-color: var(--secondary-background-color);
            border: 1px solid rgba(128, 128, 128, 0.2);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            transition: all 0.3s ease;
            cursor: pointer;
            margin-bottom: 1rem;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
        .nav-card:hover {
            transform: translateY(-5px);
            border-color: var(--primary-color);
            box-shadow: 0 10px 15px rgba(0,0,0,0.1);
            background-color: rgba(37, 99, 235, 0.05);
        }
        .nav-card i {
            font-size: 2rem;
            margin-bottom: 1rem;
            display: block;
        }
        .nav-card h4 {
            margin: 0.5rem 0;
            color: var(--text-color);
        }
        .nav-card p {
            font-size: 0.85rem;
            color: var(--text-color);
            opacity: 0.7;
            margin: 0;
        }
        </style>
    """, unsafe_allow_html=True)

    def nav_card(icon, title, subtitle, target_view):
        st.markdown(f"""
        <div class="css-card" style="text-align: center; height: 180px; display: flex; flex-direction: column; justify-content: center; align-items: center; border: 1px solid rgba(3, 105, 161, 0.1);">
            <div style="font-size: 2.2rem; margin-bottom: 5px;">{icon}</div>
            <h4 style="margin: 5px 0; color: #0F172A;">{title}</h4>
            <p style="opacity: 0.6; font-size: 0.85rem; margin-bottom: 10px;">{subtitle}</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"Open {title}", key=f"btn_nav_{target_view}", width="stretch"):
            st.session_state['current_view'] = target_view
            st.rerun()

    if app_mode == "B2B":
        c1, c2, c3 = st.columns(3)
        with c1:
            nav_card("💼", "CRM Dashboard", "Manage pipeline & leads", "CRM Dashboard")
        with c2:
            nav_card("📣", "Campaigns", "Manage outreach & ads", "Campaigns")
        with c3:
            nav_card("🕵️", "Lead Discovery", "Find new B2B prospects", "Lead Discovery")

        c4, c5, c6 = st.columns(3)
        with c4:
            nav_card("📈", "SEO Audit", "Check site health & ranking", "SEO Audit")
        with c5:
            nav_card("🤖", "Automation Hub", "Monitor autonomous missions", "Automation Hub")
        with c6:
            nav_card("⚙️", "Settings", "System configuration", "Settings")
                
    else:
        # B2C Layout
        c1, c2, c3 = st.columns(3)
        with c1:
            nav_card("🔥", "Influencer Scout", "Find viral partners", "Influencer Scout")
        with c2:
            nav_card("🎬", "Video Studio", "Create social content", "Video Studio")
        with c3:
            nav_card("⚙️", "Settings", "System configuration", "Settings")
