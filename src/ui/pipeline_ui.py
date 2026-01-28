import streamlit as st
import pandas as pd
import json
import time
from database import get_leads_by_status, create_deal, get_deals, update_deal_stage, delete_deals_bulk
from agents import ManagerAgent
from ui.components import render_data_management_bar, render_enhanced_table, render_page_chat

def render_pipeline_page():
    """Renders the Sales Pipeline UI component."""
    st.header("📂 Sales Pipeline")
    
    # CSS Fix for stage headers wrapping
    st.markdown("""
        <style>
        [data-testid="stMetricValue"] {
            font-size: 1.8rem;
        }
        .stMarkdown h3 {
            white-space: nowrap;
            font-size: 1.1rem !important;
        }
        </style>
    """, unsafe_allow_html=True)

    tab_kanban, tab_table = st.tabs(["📋 Kanban Board", "📑 Table View"])

    with tab_kanban:
        # ➕ New Deal Section
        with st.expander("➕ Create New Deal", expanded=False):
            with st.form("new_deal_form"):
                col1, col2 = st.columns(2)
                with col1:
                    d_title = st.text_input("Deal Title", placeholder="e.g. Enterprise License")
                    d_val = st.number_input("Value ($)", min_value=0.0, step=100.0)
                with col2:
                    # Fetch leads to associate
                    leads = get_leads_by_status("new") + get_leads_by_status("contacted")
                    lead_options = {f"{l.get('company_name') or 'Unknown'} ({l['email']})": l['id'] for l in leads}
                    target_lead = st.selectbox("Associate Lead", list(lead_options.keys()))
                
                if st.form_submit_button("Create Deal", type="primary"):
                    if d_title and target_lead:
                        deal_id = create_deal(lead_options[target_lead], d_title, d_val)
                        st.success(f"Deal created! (ID: {deal_id})")
                        time.sleep(1)
                        st.rerun()

        st.divider()
        deals = get_deals()
        stages = ["Discovery", "Qualification", "Proposal", "Negotiation", "Closed Won", "Closed Lost"]
        cols = st.columns(len(stages))
        for i, stage in enumerate(stages):
            with cols[i]:
                st.markdown(f"### {stage}")
                for d in [d for d in deals if d['stage'] == stage]:
                    with st.expander(f"{d['title']}", expanded=True):
                        st.write(f"${d['value']:,.0f}")
                        st.caption(f"{d.get('company_name', 'Unknown')}")
                        new_s = st.selectbox("Stage", stages, index=stages.index(stage), key=f"s_{d['id']}")
                        if new_s != stage:
                            update_deal_stage(d['id'], new_s, 50)
                            st.rerun()

    with tab_table:
        st.subheader("Manage Deals")
        deals = get_deals()
        if deals:
            deals_df = pd.DataFrame(deals)
            # 1. Standard Data Management Bar
            render_data_management_bar(deals, filename_prefix="pipeline_deals")

            # 2. Enhanced Table
            edited_deals = render_enhanced_table(deals_df, key="pipeline_deals_table")
            
            if 'Select' in edited_deals.columns:
                selected_deals = edited_deals[edited_deals['Select'] == True]
            else:
                selected_deals = pd.DataFrame()

            if not selected_deals.empty:
                if st.button(f"🗑️ Delete {len(selected_deals)} Selected Deals", type="secondary"):
                    delete_deals_bulk(selected_deals['id'].tolist())
                    st.success("Deleted!")
                    st.rerun()
        else:
            st.info("No deals in pipeline.")

    # 3. Page Level Chat
    render_page_chat(
        "Sales Pipeline", 
        ManagerAgent(), 
        json.dumps(get_deals(), indent=2)
    )
