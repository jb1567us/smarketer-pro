import streamlit as st
from ui.dashboard_ui import render_dashboard
from ui.crm_ui import render_crm_dashboard
from ui.pipeline_ui import render_pipeline_page
from ui.tasks_ui import render_tasks_page
from ui.analytics_ui import render_analytics_page
from ui.manager_ui import render_manager_ui

def render_command_tab():
    """Renders the Command & Control category views."""
    view = st.session_state.get('current_view', "Dashboard")
    
    if view == "Dashboard":
        render_dashboard()
    elif view == "CRM Dashboard":
        render_crm_dashboard()
    elif view == "Sales Pipeline":
        render_pipeline_page()
    elif view == "Task Management":
        render_tasks_page()
    elif view == "Performance Reports":
        render_analytics_page()
    elif view == "Manager Console":
        render_manager_ui()
    else:
        st.info(f"Command View '{view}' not implemented.")
