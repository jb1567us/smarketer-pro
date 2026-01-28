import streamlit as st
from ui.designer_ui import render_designer_page
from ui.video_ui import render_video_studio
from ui.hosting_ui import render_hosting_dashboard
from ui.viral_ui import render_viral_engine
from ui.creative_library_ui import render_creative_library

def render_creative_tab():
    """Renders the Creative & Assets category views."""
    view = st.session_state.get('current_view', "Designer")
    
    if view == "Designer":
        render_designer_page()
    elif view == "Video Studio":
        render_video_studio()
    elif view == "WordPress Manager":
        render_hosting_dashboard()
    elif view == "Viral Engine":
        render_viral_engine()
    elif view == "Creative Library":
        render_creative_library()
    else:
        st.info(f"Creative View '{view}' not implemented.")
