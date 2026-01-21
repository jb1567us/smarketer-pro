import streamlit as st
import subprocess
import os
import sys
import time
import json
from agents import ManagerAgent
from ui.components import render_data_management_bar, render_page_chat, premium_header, render_job_controls, render_enhanced_table, safe_action_wrapper, confirm_action
from database import get_leads, get_connection
import pandas as pd
import threading

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
             # Start in background thread? iterating generators in streamlit is tricky without blocking
             # We will use st.spinner below instead of full thread separation for simplicity in this artifact, 
             # OR adapt to use a generator that yields periodically.
             # existing 'run_agency_process' uses subprocess which blocks. 
             # We'll wrap it in the log viewer.
             st.rerun()

        def stop_mission():
             st.session_state['agency_mission_running'] = False
             # If subprocess was accessible we'd kill it.
             # For now just flag.
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
    st.subheader("📊 Mission Results (Recent Leads)")
    
    # Date Filter
    d_col1, d_col2 = st.columns([1, 4])
    with d_col1:
         days_back = st.number_input("Days Back", min_value=1, value=30, step=1)
    
    # Show leads from DB
    leads = get_leads(limit=100) # Fetch more, filter locally or update get_leads to support retention
    # Filtering by date in python for now
    if leads:
         ldf = pd.DataFrame(leads)
         # Ensure created_at is datetime
         if 'created_at' in ldf.columns:
             ldf['created_at'] = pd.to_datetime(ldf['created_at'], errors='coerce')
             cutoff = pd.Timestamp.now() - pd.Timedelta(days=days_back)
             ldf = ldf[ldf['created_at'] > cutoff]
             
         render_enhanced_table(ldf[['id', 'email', 'company_name', 'source', 'created_at']], key="agency_leads_table")
    else:
         st.info("No recent leads found. Launch a mission above!")

    # 3. Page Level Chat
    render_page_chat(
        "Agency Orchestration", 
        ManagerAgent(), 
        "Agency Architecture: Directives -> Orchestrator -> Execution Scripts"
    )

def run_agency_process(query, criteria):
    # This function blocks, but streams logs.
    # In a real async app we'd spawn a thread.
    
    # Path to orchestrator.py
    root_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
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
            encoding='utf-8' 
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
