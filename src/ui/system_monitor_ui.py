import streamlit as st
import os
import time
from datetime import datetime
try:
    import psutil
except ImportError:
    psutil = None

def render_system_monitor():
    """Renders the System Monitor UI component."""
    st.header("💻 System Monitor")
    st.caption("Live view of backend processes, agent thoughts, and system logs.")
    
    # CPU/RAM Stats
    if psutil:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        c1, c2 = st.columns(2)
        c1.metric("CPU Usage", f"{cpu}%")
        
        # RAM Color Logic
        ram_delta_color = "normal"
        if ram > 85: ram_delta_color = "inverse"
        c2.metric("RAM Usage", f"{ram}%", delta_color=ram_delta_color)
        if ram > 90:
            st.error("⚠️ High Memory Usage! Performance may degrade.")

    st.divider()
    st.subheader("📜 Live Engine Logs")
    
    # In modularized structure, we expect logs to be in the project root/logs
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    log_path = os.path.join(project_root, "logs", "engine.log")
    
    col_ctrl, col_view = st.columns([1, 4])
    with col_ctrl:
        auto_refresh = st.toggle("Auto-Refresh", value=True)
        if st.button("🗑️ Clear Logs"):
            try:
                open(log_path, 'w').close()
                st.success("Logs cleared.")
                st.rerun()
            except Exception as e:
                st.error(f"Error clearing logs: {e}")
        
        lines_to_show = st.select_slider("Lines", options=[50, 100, 200, 500, 1000], value=100)
        
    with col_view:
        log_container = st.empty()
        
        # Simple tail implementation
        try:
            if os.path.exists(log_path):
                with open(log_path, 'r', encoding='utf-8') as f:
                    # Improved: Read last N lines effectively
                    lines = f.readlines()
                    last_n = lines[-lines_to_show:]
                    log_text = "".join(last_n)
                    
                    st.code(log_text, language="log")
            else:
                st.info("Log file not found yet (waiting for startup...)")
        except Exception as e:
            st.error(f"Error reading log: {e}")
    
    if auto_refresh:
        time.sleep(2)
        st.rerun()
