import streamlit as st
import pandas as pd
from database import load_data, get_deals, get_tasks, delete_leads_bulk
from ui.components import render_enhanced_table, render_data_management_bar, render_page_chat
from agents import ManagerAgent
import json

def render_crm_dashboard():
    # (Implementing a combined view of leads and activities)
    st.header("💼 CRM Command Center")
    
    tab_overview, tab_leads = st.tabs(["📊 Overview", "📇 All Leads"])
    
    leads = load_data("leads")
    deals = get_deals()
    tasks = get_tasks(status='pending')
    
    with tab_overview:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Leads", len(leads))
        m2.metric("Active Deals", len(deals))
        m3.metric("Open Tasks", len(tasks))
        m4.metric("Pipeline Value", f"${sum(d['value'] for d in deals):,.2f}")
        
        col_l, col_r = st.columns([2, 1])
        with col_l:
            st.subheader("Recent Leads")
            if not leads.empty:
                st.dataframe(leads.tail(10), hide_index=True)
            else:
                st.info("No leads yet.")
        with col_r:
            st.subheader("Upcoming Tasks")
            if tasks:
                for t in tasks[:5]:
                    p_color = {"Low": "gray", "Medium": "blue", "High": "orange", "Urgent": "red"}.get(t.get('priority', 'Medium'), "blue")
                    st.markdown(f"• :{p_color}[{t.get('priority', 'Medium')}] {t['description']} (Due: {pd.to_datetime(t['due_date'], unit='s').strftime('%m/%d')})")
            else:
                st.write("All clear!")
    with tab_leads:
         st.subheader("Lead Database")
         if not leads.empty:
            # 1. Standard Data Management Bar
            def bulk_delete_leads():
                # We need to get selected IDs from session state or from the edited dataframe
                # However, render_enhanced_table handles the display. 
                # To handle the ACTION, we need to check the selection state.
                selected_ids = []
                if f"crm_leads_table" in st.session_state:
                    edited_data = st.session_state[f"crm_leads_table"]
                    # Streamlit data_editor returns a dict of changes or the whole df if configured
                    # We'll use the return value of render_enhanced_table below
                    pass

            # Since render_enhanced_table returns the edited df, we can use it
            valid_cols = ['id', 'company_name', 'email', 'status', 'confidence', 'tech_stack', 'source', 'created_at']
            valid_leads = leads[[c for c in valid_cols if c in leads.columns]].copy()
            
            # Action buttons for bulk
            def on_delete_leads():
                if "crm_leads_table" in st.session_state:
                    rows = st.session_state["crm_leads_table"]["edited_rows"] # This is for older streamlit or specific config
                    # Standard approach with render_enhanced_table:
                    pass
            
            # Simple approach: render bar, then table, then handle logic
            render_data_management_bar(
                leads.to_dict('records'), 
                filename_prefix="crm_leads",
                on_delete=lambda: st.warning("Please use the checkboxes and click 'Apply Delete' below (Standard UI in progress)") 
            )

            # 2. Enhanced Table
            edited_leads = render_enhanced_table(valid_leads, key="crm_leads_table")
            
            selected_leads = edited_leads[edited_leads['Select'] == True]
            if not selected_leads.empty:
                if st.button(f"🗑️ Delete {len(selected_leads)} Selected Leads", type="secondary"):
                    delete_leads_bulk(selected_leads['id'].tolist())
                    st.success("Deleted!")
                    st.rerun()

            # 3. Page Level Chat
            render_page_chat(
                "CRM Data", 
                ManagerAgent(), 
                leads.to_json(orient='records')
            )
         else:
            st.info("No leads found in database.")
