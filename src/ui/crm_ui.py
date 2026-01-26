from database import load_data, get_deals, get_tasks, delete_leads_bulk, update_lead, get_connection
from ui.components import render_enhanced_table, render_data_management_bar, render_page_chat, safe_action_wrapper, confirm_action, premium_header
import json
from datetime import datetime
import streamlit as st
import pandas as pd

def render_crm_dashboard():
    premium_header("💼 CRM Command Center", "Orchestrate your sales pipeline, manage prospect relationships, and track outreach performance.")
    
    st.sidebar.markdown("### 📅 Pipeline Filters")
    min_date = datetime(2024, 1, 1)
    date_range = st.sidebar.date_input("Filter Data Range", [min_date, datetime.now()], key="crm_date_filter")
    
    st.sidebar.divider()
    st.sidebar.markdown("### ➕ Lead Actions")
    
    # 1. Manual Lead Creation
    with st.sidebar.expander("Add Single Lead", expanded=False):
        with st.form("create_lead_form"):
            new_name = st.text_input("Contact Name *")
            new_company = st.text_input("Company Name")
            new_email = st.text_input("Email Address *")
            new_status = st.selectbox("Initial Status", ["new", "contacted", "qualifying", "replied", "nurtured"])
            
            if st.form_submit_button("Save Lead"):
                import re
                email_regex = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
                
                if not new_name.strip():
                     st.error("Contact Name is required.")
                elif not new_email.strip() or not re.match(email_regex, new_email):
                     st.error("Valid Email Address is required.")
                else:
                     # Check for duplicates (basic check)
                     leads_check = load_data("leads")
                     if not leads_check.empty and new_email in leads_check['email'].values:
                         st.error(f"Lead with email {new_email} already exists.")
                     else:
                         from database import create_lead
                         create_lead({
                             "contact_person": new_name,
                             "company_name": new_company,
                             "email": new_email,
                             "status": new_status,
                             "created_at": datetime.now().isoformat()
                         })
                         st.success(f"Added {new_name}!")
                         st.rerun()

    # 2. CSV Import
    with st.sidebar.expander("Import Leads (CSV)", expanded=False):
        up_file = st.file_uploader("Upload CSV", type=["csv"])
        if up_file:
            if st.button("Process Import"):
                try:
                    df = pd.read_csv(up_file)
                    required_cols = {"email", "contact_person"}  # Minimal requirement
                    if not required_cols.issubset(df.columns):
                        st.error(f"CSV must contain columns: {required_cols}")
                    else:
                        from database import create_lead
                        success_count = 0
                        for _, row in df.iterrows():
                            # Basic validation per row
                            if pd.isna(row.get('email')) or pd.isna(row.get('contact_person')):
                                continue
                                
                            create_lead({
                                "contact_person": row.get('contact_person'),
                                "company_name": row.get('company_name', 'Unknown'),
                                "email": row.get('email'),
                                "status": row.get('status', 'new'),
                                "created_at": datetime.now().isoformat()
                            })
                            success_count += 1
                        st.success(f"Successfully imported {success_count} leads!")
                        st.rerun()
                except Exception as e:
                    st.error(f"Import failed: {e}")
    
    tab_overview, tab_leads = st.tabs(["📊 Overview", "📇 All Leads"])
    
    # Load Data
    leads = load_data("leads")
    deals = get_deals()
    tasks = get_tasks(status='pending')
    
    # Apply Date Filters (Basic implementation assuming 'created_at' or similar exists)
    # If leads have timestamps, filter them. For now, we just load all to avoid complexity if columns miss.
    
    with tab_overview:
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Leads", len(leads))
        m2.metric("Active Deals", len(deals))
        m3.metric("Open Tasks", len(tasks))
        val = sum(d['value'] for d in deals) if deals else 0.0
        m4.metric("Pipeline Value", f"${val:,.2f}")
        
        col_l, col_r = st.columns([2, 1])
        with col_l:
            st.subheader("Recent Leads")
            if not leads.empty:
                # Show last 5
                st.dataframe(leads.tail(5), hide_index=True, width="stretch")
            else:
                st.info("No leads yet.")
        with col_r:
            st.subheader("Upcoming Tasks")
            if tasks:
                for t in tasks[:5]:
                    p_color = {"Low": "gray", "Medium": "blue", "High": "orange", "Urgent": "red"}.get(t.get('priority', 'Medium'), "blue")
                    st.markdown(f"• :{p_color}[{t.get('priority', 'Medium')}] {t['description']}")
            else:
                st.success("All tasks cleared!")

    with tab_leads:
        st.subheader("📇 Lead Database")
        
        if leads.empty:
            st.info("No leads found in database. Go to 'Lead Discovery' to find some!")
        else:
            # 1. Search Bar
            search_q = st.text_input("🔍 Search Leads", placeholder="Company, Contact, or Email...", key="crm_main_search")
            
            display_leads = leads.copy()
            if search_q:
                # Filter by multiple columns
                mask = (
                    display_leads['company_name'].astype(str).str.contains(search_q, case=False, na=False) |
                    display_leads['contact_person'].astype(str).str.contains(search_q, case=False, na=False) |
                    display_leads['email'].astype(str).str.contains(search_q, case=False, na=False)
                )
                display_leads = display_leads[mask]

            # 2. Bulk Actions
            col_b1, col_b2 = st.columns([1, 4])
            
            # 3. Main Table
            # We want to allow selecting rows to view details AND bulk actions.
            # render_enhanced_table supports 'Select' col.
            
            st.caption(f"Showing {len(display_leads)} leads")
            leads_with_selection = render_enhanced_table(
                display_leads[['id', 'company_name', 'contact_person', 'email', 'status', 'confidence']], 
                key="crm_leads_table"
            )
            
            selected_ids = leads_with_selection[leads_with_selection['Select'] == True]['id'].tolist() if 'Select' in leads_with_selection.columns else []
            
            # Bulk Action Bar (appears if selected)
            if selected_ids:
                with st.container(border=True):
                    st.markdown(f"**Bulk Actions ({len(selected_ids)} Selected)**")
                    bc1, bc2 = st.columns(2)
                    with bc1:
                        new_status_bulk = st.selectbox("Update Status", ["new", "contacted", "qualifying", "replied", "nurtured"], key="bulk_st_sel")
                        if st.button("Apply Status"):
                             safe_action_wrapper(lambda: [update_lead(lid, {"status": new_status_bulk}) for lid in selected_ids], f"Updated {len(selected_ids)} leads.")
                             st.rerun()
                    with bc2:
                        def bulk_del():
                             delete_leads_bulk(selected_ids)
                        confirm_action("🗑️ Delete Selected", f"Delete {len(selected_ids)} records?", bulk_del, key="crm_bulk_del")
            
            st.divider()

            # 4. Detail View (if EXACTLY ONE is selected, show details below. If multiple, show bulk above. If none, show nothing or filtered.)
            # Actually, standard user flow is: Click row -> Open details.
            # But with checkboxes, maybe we assume "View Details" button for the first selected?
            # Or we use a separate "Select to View" box.
            
            # Let's use the first selected ID for details if available.
            detail_id = selected_ids[0] if len(selected_ids) == 1 else None
            
            if len(selected_ids) > 1:
                st.info("Select a single row to view full details.")
            elif detail_id:
                # Fetch fresh data for that lead
                # We can grab from dataframe
                row = leads[leads['id'] == detail_id].iloc[0]
                
                with st.container(border=True):
                    st.markdown(f"### 👤 {row.get('contact_person', 'Unknown')} @ {row.get('company_name', 'Unknown')}")
                    
                    d_c1, d_c2_d_c3 = st.columns([2, 1])
                    with d_c1:
                         st.write(f"**Email:** {row.get('email')}")
                         st.write(f"**Source:** {row.get('source', 'Unknown')}")
                         
                         # Atomic Status Update
                         def on_status_change():
                             # This callback handles the state change immediately
                             new_st = st.session_state[f"st_change_{detail_id}"]
                             update_lead(detail_id, {"status": new_st})
                             st.toast(f"Status updated to {new_st}")
                             
                         st.selectbox(
                             "**Status:**", 
                             ["new", "contacted", "qualifying", "replied", "nurtured"],
                             index=["new", "contacted", "qualifying", "replied", "nurtured"].index(row.get('status', 'new')),
                             key=f"st_change_{detail_id}",
                             on_change=on_status_change
                         )
                    
                    t_notes, t_actions, t_log = st.tabs(["📝 Notes", "⚡ Actions", "📞 Log Interaction"])
                    
                    with t_notes:
                         current_notes = row.get('notes', "")
                         new_notes = st.text_area("Notes", value=current_notes or "", key=f"note_{detail_id}")
                         if st.button("Save Notes", key=f"sv_note_{detail_id}"):
                             update_lead(detail_id, {"notes": new_notes})
                             st.toast("Notes saved!")
                             st.rerun()
                             
                    with t_actions:
                         if st.button("🚀 Launch Outreach Campaign", key=f"lc_{detail_id}"):
                             # Set session state to prep campaign UI
                             st.session_state['launch_campaign_lead_id'] = detail_id
                             st.success(f"Prepared campaign for {row.get('contact_person')}. Switch to 'Campaigns' tab to finalize.")
                         
                         def del_single():
                             delete_leads_bulk([detail_id])
                             st.session_state['crm_refresh_trigger'] = datetime.now() # Force refresh
                         
                         st.markdown("---")
                         confirm_action("🗑️ Delete Lead", "Remove this lead permanently?", del_single, key=f"del_s_{detail_id}")

                    with t_log:
                        with st.form(f"log_int_{detail_id}"):
                            i_type = st.selectbox("Interaction Type", ["Email", "Call", "LinkedIn", "Meeting"])
                            i_date = st.date_input("Date", datetime.now())
                            i_notes = st.text_area("Summary")
                            
                            if st.form_submit_button("Log Interaction"):
                                # In a real app, we'd save this to a sub-table.
                                # For now, we append to notes or just toast standardly.
                                timestamp = f"{i_date} [{i_type}]"
                                append_note = f"\n\n-- {timestamp} --\n{i_notes}"
                                current_full_notes = row.get('notes', "") + append_note
                                update_lead(detail_id, {"notes": current_full_notes})
                                st.success("Interaction logged!")
                                st.rerun()
            else:
                st.caption("Select a single row in the table above to view details/notes.")
