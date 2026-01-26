
import streamlit as st
import subprocess
import os
import sys
import time
import json
import pandas as pd
from agents import ManagerAgent
from ui.components import render_data_management_bar, render_page_chat, premium_header, render_job_controls, render_enhanced_table, safe_action_wrapper, confirm_action
from database import get_leads, delete_lead
from datetime import datetime

def render_agency_ui():
    premium_header("🤖 Agency Orchestrator", "Direct control over the 3-Layer Agency Architecture: Directives -> Orchestrator -> Execution.")

    # --- 1. CONFIGURATION SECTION ---
    with st.expander("📝 Directives (Standard Operating Procedures)", expanded=False):
        d_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'directives')
        
        # Helper to load/save
        def load_directive(name):
            try:
                with open(os.path.join(d_path, f"{name}.md"), 'r', encoding='utf-8') as f:
                    return f.read()
            except: return ""
            
        def save_directive(name, content):
            if not content.strip():
                 st.warning(f"Content for {name} cannot be empty.")
                 return
            def _write():
                 with open(os.path.join(d_path, f"{name}.md"), 'w', encoding='utf-8') as f:
                    f.write(content)
            safe_action_wrapper(_write, f"Saved {name}.md")

        def delete_directive(name):
             def _del():
                 p = os.path.join(d_path, f"{name}.md")
                 if os.path.exists(p):
                     os.remove(p)
                     # Reset to default or empty
                     with open(p, 'w', encoding='utf-8') as f: f.write("")
             safe_action_wrapper(_del, f"Reset {name}.md to empty.")

        tabs = st.tabs(["Discovery", "Qualification", "Enrichment", "Handover"])
        
        tab_map = {
             0: "discovery",
             1: "qualification",
             2: "enrichment",
             3: "handover"
        }
        
        for i, tname in tab_map.items():
            with tabs[i]:
                c = st.text_area(f"{tname.title()} Logic", value=load_directive(tname), height=300, key=f"d_{tname}")
                c1, c2 = st.columns([1, 4])
                with c1:
                     if st.button(f"💾 Save {tname.title()}", key=f"btn_save_{tname}"):
                          save_directive(tname, c)
                with c2:
                     confirm_action(f"🗑️ Reset {tname}", "Clear this directive?", lambda: delete_directive(tname), key=f"rst_{tname}")

    st.divider()

    # --- 2. MISSION CONTROL ---
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_input("Mission Goal / Query", placeholder="e.g. Find Solar Panel Installers in Austin")
        criteria = st.text_area("Specific Criteria (Overrides Qualification Directive)", height=100, 
                                placeholder="Must be residential focus. Must have a working website.",
                                help="Enter specific rules that override the standard Qualification Directive. E.g. 'Must use Shopify'.")
    
    with col2:
        st.markdown("### Action")
        # Check if running
        is_running = st.session_state.get('agency_mission_running', False)
        
        def start_mission():
             if not query:
                 st.error("Please enter a query.")
                 return
             st.session_state['agency_mission_running'] = True
             st.session_state['agency_mission_logs'] = []
             st.toast("Mission Initiated!", icon="🚀")
             st.rerun()

        def stop_mission():
             st.session_state['agency_mission_running'] = False
             st.toast("Stopping Mission...", icon="🛑")
             st.rerun()

        render_job_controls(
             "Mission Orchestrator", 
             is_running=is_running,
             on_start=start_mission,
             on_stop=stop_mission,
             status_text="Mission in progress..." if is_running else "Ready to Launch"
        )
        
    if st.session_state.get('agency_mission_running', False):
         run_agency_process(query, criteria)

    st.divider()
    st.subheader("📊 Mission Results & Lead Management")
    
    # Filters & Search
    f_col1, f_col2, f_col3 = st.columns([1, 2, 1])
    with f_col1:
         days_back = st.number_input("Days Back", min_value=1, value=30, step=1)
    with f_col2:
         search_term = st.text_input("Search Leads", placeholder="Search by Company, Email, or Source...")
    
    # Show leads from DB
    leads = get_leads(limit=500) 
    
    if leads:
         ldf = pd.DataFrame(leads)
         
         # 1. Date Filter
         if 'created_at' in ldf.columns:
             ldf['created_at'] = pd.to_datetime(ldf['created_at'], errors='coerce')
             cutoff = pd.Timestamp.now() - pd.Timedelta(days=days_back)
             ldf = ldf[ldf['created_at'] > cutoff]
         
         # 2. Search Filter
         if search_term and not ldf.empty:
             term = search_term.lower()
             ldf = ldf[ldf.apply(lambda row: 
                 term in str(row.get('company_name', '')).lower() or 
                 term in str(row.get('email', '')).lower() or
                 term in str(row.get('source', '')).lower(), axis=1)]

         # 3. Pagination & Display
         if not ldf.empty:
             # Pagination
             ROWS_PER_PAGE = 10
             total_rows = len(ldf)
             total_pages = (total_rows - 1) // ROWS_PER_PAGE + 1
             
             if 'agency_page' not in st.session_state: st.session_state['agency_page'] = 1
             
             # Adjust page if out of bounds
             if st.session_state['agency_page'] > total_pages: st.session_state['agency_page'] = total_pages
             
             start_idx = (st.session_state['agency_page'] - 1) * ROWS_PER_PAGE
             end_idx = start_idx + ROWS_PER_PAGE
             
             # Display Page
             page_df = ldf.iloc[start_idx:end_idx].copy()
             
             # Add selection column for bulk actions if render_enhanced_table doesn't support it natively in this context
             # We'll use a standard data_editor with selection for robustness
             
             # Action Toolbar
             p_col1, p_col2, p_col3 = st.columns([2, 5, 2])
             with p_col1:
                 st.write(f"Showing {start_idx+1}-{min(end_idx, total_rows)} of {total_rows}")
             with p_col3:
                 # prev/next
                 pn_c1, pn_c2 = st.columns(2)
                 if pn_c1.button("◀", disabled=st.session_state['agency_page']==1):
                     st.session_state['agency_page'] -= 1
                     st.rerun()
                 if pn_c2.button("▶", disabled=st.session_state['agency_page']==total_pages):
                     st.session_state['agency_page'] += 1
                     st.rerun()

             # Table
             page_df['Select'] = False
             cols = ['Select', 'id', 'company_name', 'email', 'source', 'created_at']
             # Reorder if columns exist
             cols = [c for c in cols if c in page_df.columns or c == 'Select']
             
             edited_page = st.data_editor(
                 page_df[cols],
                 column_config={
                     "Select": st.column_config.CheckboxColumn(required=True),
                     "created_at": st.column_config.DatetimeColumn("Created"),
                     "email": st.column_config.textColumn("Email"),
                     "company_name": st.column_config.textColumn("Company"),
                 },
                 disabled=["id", "company_name", "email", "source", "created_at"],
                 hide_index=True,
                 key="agency_leads_editor"
             )
             
             # Bulk Actions
             selected_rows = edited_page[edited_page['Select'] == True]
             
             if not selected_rows.empty:
                 ba_col1, ba_col2 = st.columns(2)
                 with ba_col1:
                     if st.button(f"🗑️ Delete {len(selected_rows)} Leads"):
                         confirm_action("Confirm Delete", f"Permanently delete {len(selected_rows)} items?", 
                                        lambda: [delete_lead(rid) for rid in selected_rows['id'].tolist()], 
                                        key="bulk_del")
                 with ba_col2:
                     csv = selected_rows.drop(columns=['Select']).to_csv(index=False)
                     st.download_button("📥 Export Selected", data=csv, file_name="selected_leads.csv", mime="text/csv")

         else:
             st.info("No leads match your search filters.")
    else:
         st.info("No leads found in database. Launch a mission above!")

    # 3. Page Level Chat
    render_page_chat(
        "Agency Orchestration", 
        ManagerAgent(), 
        "Agency Architecture: Directives -> Orchestrator -> Execution Scripts"
    )

def run_agency_process(query, criteria):
    # This function blocks, but streams logs.
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    orch_path = os.path.join(root_dir, "orchestrator.py")
    
    cmd = [sys.executable, "-u", orch_path, query] 
    if criteria:
        cmd.extend(["--criteria", criteria])
        
    log_container = st.container(border=True)
    log_container.caption("📜 Mission Logic Stream")
    log_text = st.empty()
    
    logs = []
    
    try:
        process = subprocess.Popen(
            cmd,
            cwd=root_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            encoding='utf-8',
            errors='replace'
        )
        
        # Stream output
        while True:
            # Check stop flag
            if not st.session_state.get('agency_mission_running', True):
                process.terminate()
                st.warning("Mission aborted by user.")
                break

            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                logs.append(line.rstrip())
                # Update UI
                log_text.code("\n".join(logs[-15:]), language="bash")
        
        # Log Export
        st.download_button("📥 Download Mission Logs", data="\n".join(logs), file_name="mission_logs.txt")
                
        if process.returncode == 0:
            st.success("Mission Complete!")
            st.session_state['agency_mission_running'] = False
            # Trigger rerun to show leads
            time.sleep(1)
            st.rerun()
        elif process.returncode is not None and process.returncode != 0:
             # Only show error if not manually killed
             if st.session_state.get('agency_mission_running', True):
                st.error("Mission failed with errors.")
                st.session_state['agency_mission_running'] = False

    except Exception as e:
        st.error(f"Failed to start process: {e}")
        st.session_state['agency_mission_running'] = False
