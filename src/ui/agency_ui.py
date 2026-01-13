import streamlit as st
import subprocess
import os
import sys
import time
import json
from agents import ManagerAgent
from ui.components import render_data_management_bar, render_page_chat

def render_agency_ui():
    st.header("🤖 Agency Orchestrator")
    st.caption("Direct control over the 3-Layer Agency Architecture: Directives -> Orchestrator -> Execution.")

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
            with open(os.path.join(d_path, f"{name}.md"), 'w', encoding='utf-8') as f:
                f.write(content)
            st.toast(f"Saved {name}.md")

        tabs = st.tabs(["Discovery", "Qualification", "Enrichment", "Handover"])
        
        with tabs[0]:
            c = st.text_area("Discovery Logic", value=load_directive("discovery"), height=300, key="d_discovery")
            if st.button("Save Discovery", key="btn_save_disc"): save_directive("discovery", c)
            
        with tabs[1]:
            c = st.text_area("Qualification Logic", value=load_directive("qualification"), height=300, key="d_qual")
            if st.button("Save Qualification", key="btn_save_qual"): save_directive("qualification", c)

        with tabs[2]:
            c = st.text_area("Enrichment Logic", value=load_directive("enrichment"), height=300, key="d_enrich")
            if st.button("Save Enrichment", key="btn_save_enrich"): save_directive("enrichment", c)

        with tabs[3]:
            c = st.text_area("Handover Logic", value=load_directive("handover"), height=300, key="d_hand")
            if st.button("Save Handover", key="btn_save_hand"): save_directive("handover", c)

    st.divider()

    # --- 2. MISSION CONTROL ---
    col1, col2 = st.columns([3, 1])
    
    with col1:
        query = st.text_input("Mission Goal / Query", placeholder="e.g. Find Solar Panel Installers in Austin")
        criteria = st.text_area("Specific Criteria (Overrides Qualification Directive)", height=100, placeholder="Must be residential focus. Must have a working website.")
    
    with col2:
        st.markdown("### Action")
        if st.button("🚀 Launch Mission", type="primary", use_container_width=True):
            if not query:
                st.error("Please enter a query.")
                return
            
            # RUN LOGIC
            run_agency_process(query, criteria)

    # 3. Page Level Chat
    render_page_chat(
        "Agency Orchestration", 
        ManagerAgent(), 
        "Agency Architecture: Directives -> Orchestrator -> Execution Scripts"
    )

def run_agency_process(query, criteria):
    st.info("Spinning up Orchestrator...")
    
    # Path to orchestrator.py
    # We are in src/ui/agency_ui.py -> ../../orchestrator.py
    root_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    orch_path = os.path.join(root_dir, "orchestrator.py")
    
    cmd = [sys.executable, "-u", orch_path, query] # -u for unbuffered
    if criteria:
        cmd.extend(["--criteria", criteria])
        
    log_placeholder = st.empty()
    logs = []
    
    try:
        process = subprocess.Popen(
            cmd,
            cwd=root_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            encoding='utf-8' # Force encoding
        )
        
        # Stream output
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                logs.append(line.rstrip())
                # Update UI every few lines or just always
                log_placeholder.code("\n".join(logs[-20:]), language="bash") # Show last 20 lines
                
        if process.returncode == 0:
            st.success("Mission Complete! Check 'All Leads' in CRM.")
        else:
            st.error("Mission failed with errors.")
            
    except Exception as e:
        st.error(f"Failed to start process: {e}")
