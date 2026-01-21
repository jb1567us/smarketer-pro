from database import load_data, get_deals, get_tasks, delete_leads_bulk, update_lead, get_connection
from ui.components import render_enhanced_table, render_data_management_bar, render_page_chat, safe_action_wrapper, confirm_action, premium_header
import json
from datetime import datetime
import time

def render_crm_dashboard():
    premium_header("💼 CRM Command Center", "Orchestrate your sales pipeline, manage prospect relationships, and track outreach performance.")
    
    # Global Date Filter
    st.sidebar.markdown("### 📅 Pipeline Filters")
    date_range = st.sidebar.date_input("Filter Data Range", [datetime(2026, 1, 1), datetime.now()], key="crm_date_filter")
    
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
            # --- Bulk Action Bar ---
            col_b1, col_b2, col_b3 = st.columns([1, 1, 4])
            with col_b1:
                st.markdown(" ") # Spacer
            
            # --- LIST VIEW WITH ENHANCED TABLE ---
            st.markdown("#### Selection & Bulk Actions")
            leads_with_selection = render_enhanced_table(leads[['id', 'company_name', 'contact_person', 'status', 'confidence']], key="leads_table")
            
            selected_ids = leads_with_selection[leads_with_selection['Select'] == True]['id'].tolist()
            
            if selected_ids:
                with st.container(border=True):
                    st.write(f"Selected **{len(selected_ids)}** leads")
                    cb1, cb2 = st.columns(2)
                    with cb1:
                        def bulk_del():
                            delete_leads_bulk(selected_ids)
                        
                        confirm_action("🗑️ Bulk Delete", f"Delete {len(selected_ids)} leads permanently?", bulk_del, key="bulk_del")
                    with cb2:
                        new_status_bulk = st.selectbox("Set Status to:", ["new", "contacted", "qualifying", "replied", "nurtured"], key="bulk_status_sel")
                        if st.button("Apply Status"):
                            safe_action_wrapper(lambda: [update_lead(lid, {"status": new_status_bulk}) for lid in selected_ids], f"Updated {len(selected_ids)} leads to {new_status_bulk}")
                            st.rerun()

            st.divider()
            
            # --- DETAIL VIEW (Single Select) ---
            st.markdown("#### Lead Details & Interaction")
            col_list_mini, col_details = st.columns([1, 2])
            
            with col_list_mini:
                search_q = st.text_input("Quick Lookup", placeholder="Filter by name...", key="crm_search")
                display_leads = leads.copy()
                if search_q:
                    display_leads = display_leads[display_leads['company_name'].str.contains(search_q, case=False, na=False)]
                
                # Selection for details
                event = st.dataframe(
                    display_leads[['company_name', 'status']],
                    use_container_width=True,
                    hide_index=True,
                    on_select="rerun",
                    selection_mode="single-row",
                    key="crm_mini_list"
                )
                
                selected_row = None
                if event.selection.rows:
                    idx = event.selection.rows[0]
                    selected_row = display_leads.iloc[idx]
            
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
                            current_notes = selected_row.get('notes', "")
                            new_notes = st.text_area("Record History & Strategic Notes", value=current_notes or "", height=150, key=f"note_area_{selected_row['id']}")
                            if st.button("💾 Save Notes", use_container_width=True):
                                safe_action_wrapper(lambda: update_lead(selected_row['id'], {"notes": new_notes}), "Lead notes updated successfully!")
                                st.rerun()
                                
                        with t_actions:
                            st.write("### ⚡ Engagement Workflow")
                            
                            # CTAs
                            ca_c1, ca_c2 = st.columns(2)
                            with ca_c1:
                                if st.button("🚀 Launch Campaign", use_container_width=True, type="primary"):
                                    st.session_state['current_view'] = "Campaigns"
                                    # Logic to pre-select this lead in campaign UI could be added
                                    st.rerun()
                            with ca_c2:
                                if st.button("📄 Generate DSR", use_container_width=True):
                                    st.session_state['current_view'] = "Digital Sales Room"
                                    st.rerun()
                            
                            st.divider()
                            st.markdown("**Core Management**")
                            current_status = selected_row.get('status', 'new').lower()
                            possible_statuses = ["new", "contacted", "qualifying", "replied", "nurtured", "closed won", "closed lost"]
                            
                            new_status = st.selectbox("Update Pipeline Status", 
                                [s.capitalize() for s in possible_statuses],
                                index=possible_statuses.index(current_status) if current_status in possible_statuses else 0
                            )
                            if st.button("Confirm Status Change", use_container_width=True):
                                safe_action_wrapper(lambda: update_lead(selected_row['id'], {"status": new_status.lower()}), f"Status updated to {new_status}")
                                st.rerun()
                            
                            st.divider()
                            def single_del():
                                delete_leads_bulk([selected_row['id']])
                            
                            confirm_action("🗑️ Delete Record", f"Permanently remove {selected_row.get('company_name')} from the database?", single_del, key=f"del_{selected_row['id']}")

                else:
                    st.info("👈 Select a lead from the list to view details.")
