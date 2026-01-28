import streamlit as st
from ui.campaign_ui import render_campaign_page
from ui.lead_discovery_ui import render_lead_discovery
from ui.social_hub_ui import render_social_scheduler_page, render_social_pulse_page
from ui.affiliate_ui import render_affiliate_ui
from ui.dsr_ui import render_dsr_page

def render_outreach_tab():
    """Renders the Outreach & Campaigns category views."""
    view = st.session_state.get('current_view', "Campaigns")
    
    if view == "Campaigns":
        render_campaign_page()
    elif view == "Lead Discovery":
        render_lead_discovery()
    elif view == "Social Scheduler":
        render_social_scheduler_page()
    elif view == "Social Pulse":
        render_social_pulse_page()
    elif view == "Affiliate Hub":
        render_affiliate_ui()
    elif view == "DSR Manager":
        render_dsr_page()
    else:
        st.info(f"Outreach View '{view}' not implemented.")
