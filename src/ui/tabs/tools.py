import streamlit as st
from ui.agent_lab_ui import render_agent_lab
from ui.automation_ui import render_automation_hub, render_workflow_builder
from ui.agent_factory_ui import render_agent_factory
from ui.seo_ui import render_seo_audit, render_keyword_research, render_link_wheel_builder
from ui.mass_tools_ui import render_mass_tools_page
from ui.proxy_lab_ui import render_proxy_lab
from ui.system_monitor_ui import render_system_monitor

def render_tools_tab():
    """Renders the Technical Tools & Utilities category views."""
    view = st.session_state.get('current_view', "Agent Lab")
    
    if view == "Agent Lab":
        render_agent_lab()
    elif view == "Automation Hub":
        render_automation_hub()
    elif view == "Workflow Builder":
        render_workflow_builder()
    elif view == "Agent Factory":
        render_agent_factory()
    elif view == "SEO Audit":
        render_seo_audit()
    elif view == "Keyword Research":
        render_keyword_research()
    elif view == "Link Wheel Builder":
        render_link_wheel_builder()
    elif view == "Mass Tools":
        render_mass_tools_page()
    elif view == "Proxy Lab":
        render_proxy_lab()
    elif view == "System Monitor":
        render_system_monitor()
    elif view == "Analytics":
        from ui.analytics_dashboard import render_analytics_dashboard
        render_analytics_dashboard()
    elif view == "Scheduler":
        from ui.scheduler_ui import render_scheduler_ui
        render_scheduler_ui()
    elif view == "Webhooks":
        from ui.webhooks_ui import render_webhooks_ui
        render_webhooks_ui()
    else:
        st.info(f"Tools View '{view}' not implemented.")
