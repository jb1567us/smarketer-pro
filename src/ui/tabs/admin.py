import streamlit as st
from ui.settings_ui import render_settings_page

def render_admin_tab():
    """Renders the Admin & Settings category views."""
    view = st.session_state.get('current_view', "Settings")
    
    if view == "Settings":
        render_settings_page()
    else:
        st.info(f"Admin View '{view}' not implemented.")
