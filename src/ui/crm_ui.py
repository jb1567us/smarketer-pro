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
        st.subheader("📇 Lead Database")
        
        if leads.empty:
            st.info("No leads found in database. Go to 'Lead Discovery' to find some!")
        else:
            # Layout: Left Panel (List/Filters), Right Panel (Details)
            col_list, col_details = st.columns([1, 1.5])
            
            # --- LEFT PANEL: LIST & FILTERS ---
            with col_list:
                status_filter = st.multiselect(
                    "Filter Status", 
                    options=leads['status'].unique() if 'status' in leads.columns else [],
                    default=[]
                )
                
                # Apply filter
                filtered_leads = leads.copy()
                if status_filter:
                    filtered_leads = filtered_leads[filtered_leads['status'].isin(status_filter)]
                
                # Search
                search_q = st.text_input("Search Leads", placeholder="Company, Email...")
                if search_q:
                    filtered_leads = filtered_leads[
                        filtered_leads['company_name'].astype(str).str.contains(search_q, case=False) |
                        filtered_leads['email'].astype(str).str.contains(search_q, case=False)
                    ]
                
                st.caption(f"Showing {len(filtered_leads)} leads")
                
                # Selection List
                # We use a dataframe with selection mode for the master list
                event = st.dataframe(
                    filtered_leads[['company_name', 'contact_person', 'status', 'confidence']],
                    use_container_width=True,
                    hide_index=True,
                    on_select="rerun",
                    selection_mode="single-row"
                )
                
                selected_row = None
                if event.selection.rows:
                    idx = event.selection.rows[0]
                    selected_row = filtered_leads.iloc[idx]
            
            # --- RIGHT PANEL: DETAILS ---
            with col_details:
                if selected_row is not None:
                    with st.container(border=True):
                        # Header
                        c_h1, c_h2 = st.columns([3, 1])
                        with c_h1:
                            st.markdown(f"## {selected_row.get('company_name') or 'Unknown Company'}")
                            st.caption(f"👤 {selected_row.get('contact_person') or 'No Contact Name'} | 📧 {selected_row.get('email')}")
                        with c_h2:
                            st.metric("Score", f"{selected_row.get('confidence', 0)}%")
                        
                        st.divider()
                        
                        # Tabs for Detail View
                        t_info, t_notes, t_actions = st.tabs(["ℹ️ Info", "📝 Notes", "⚡ Actions"])
                        
                        with t_info:
                            st.markdown("**Details**")
                            # Safely display other fields
                            exclude = ['company_name', 'email', 'contact_person', 'confidence', 'id']
                            for k, v in selected_row.to_dict().items():
                                if k not in exclude and v:
                                    st.text(f"{k.replace('_', ' ').capitalize()}: {v}")
                                    
                        with t_notes:
                            # Placeholder for notes system (could be a separate table in future)
                            current_notes = st.session_state.get(f"notes_{selected_row['id']}", "")
                            new_notes = st.text_area("Lead Notes", value=current_notes, height=150, key=f"note_area_{selected_row['id']}")
                            if st.button("Save Notes"):
                                st.session_state[f"notes_{selected_row['id']}"] = new_notes
                                st.success("Notes saved (locally)!")
                                
                        with t_actions:
                            st.write("Manage this relationship")
                            current_status = selected_row.get('status', 'New')
                            new_status = st.selectbox("Update Status", 
                                ["New", "Contacted", "Qualifying", "Replied", "Closed Won", "Closed Lost"],
                                index=0 # Logic to match index would go here
                            )
                            if st.button("Update Status"):
                                # Dummy update
                                st.toast(f"Status updated to {new_status}")
                            
                            st.divider()
                            if st.button("🗑️ Delete Lead", type="primary"):
                                delete_leads_bulk([selected_row['id']])
                                st.rerun()

                else:
                    st.info("👈 Select a lead from the list to view details.")
