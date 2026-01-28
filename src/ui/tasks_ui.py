import streamlit as st
import pandas as pd
import time
import json
from datetime import datetime
from database import get_tasks, create_task, mark_task_completed, delete_task, load_data
from agents import ManagerAgent
from ui.components import render_page_chat

def render_tasks_page():
    """Renders the Task Management UI component."""
    st.header("📝 Task Management")
    
    # Load data
    all_tasks = get_tasks()
    pending_tasks = [t for t in all_tasks if t['status'] == 'pending']
    completed_tasks = [t for t in all_tasks if t['status'] == 'completed']
    overdue_tasks = [t for t in pending_tasks if t.get('due_date', 0) < time.time()]
    
    # Dashboard Stats
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Total Tasks", len(all_tasks))
    s2.metric("Pending", len(pending_tasks))
    s3.metric("Completed", len(completed_tasks))
    s4.metric("Overdue", len(overdue_tasks), delta_color="inverse")
    
    st.divider()
    
    # Create Task Form
    with st.expander("➕ Create New Task", expanded=len(all_tasks) == 0):
        with st.form("new_task_form"):
            col1, col2 = st.columns(2)
            with col1:
                description = st.text_input("Task Description", placeholder="e.g. Follow up on proposal")
                priority = st.selectbox("Priority", ["Low", "Medium", "High", "Urgent"], index=1)
            with col2:
                task_type = st.selectbox("Type", ["Call", "Email", "Meeting", "Research", "Follow-up", "Task"], index=5)
                due_date = st.date_input("Due Date")
            
            # Associated Lead
            leads_list = load_data("leads")
            lead_options = {"None": None}
            if not leads_list.empty:
                for _, row in leads_list.iterrows():
                    label = f"{row['company_name']} ({row['contact_person']})" if row.get('company_name') else row['email']
                    lead_options[label] = row['id']
            
            selected_lead_label = st.selectbox("Associate with Lead", list(lead_options.keys()))
            lead_id = lead_options[selected_lead_label]
            
            if st.form_submit_button("Create Task", width="stretch"):
                if description:
                    # Convert date to timestamp
                    dt = datetime.combine(due_date, datetime.min.time())
                    ts = int(dt.timestamp())
                    create_task(lead_id, description, ts, priority, task_type)
                    st.success("Task created!")
                    st.rerun()
                else:
                    st.error("Please enter a description.")

    # View Tasks
    tab_active, tab_completed = st.tabs(["📋 Active Tasks", "✅ Completed"])
    
    with tab_active:
        if not pending_tasks:
            st.info("No active tasks. Time to relax!")
        else:
            for t in pending_tasks:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([0.1, 3, 1])
                    
                    # Priority indicator
                    p_color = {"Low": "gray", "Medium": "blue", "High": "orange", "Urgent": "red"}.get(t['priority'], "blue")
                    
                    with c2:
                        st.markdown(f"**{t['description']}**")
                        lead_name = t.get('company_name') or "General Task"
                        st.caption(f"📌 {t['task_type']} | 🏢 {lead_name} | 📅 Due: {pd.to_datetime(t.get('due_date', 0), unit='s').strftime('%Y-%m-%d')}")
                    
                    with c3:
                        st.markdown(f":{p_color}[{t['priority']}]")
                        col_b1, col_b2 = st.columns(2)
                        if col_b1.button("Done", key=f"done_{t['id']}"):
                            mark_task_completed(t['id'])
                            st.rerun()
                        if col_b2.button("🗑️", key=f"del_{t['id']}"):
                            delete_task(t['id'])
                            st.rerun()

    with tab_completed:
        if not completed_tasks:
            st.write("No completed tasks yet.")
        else:
            for t in completed_tasks:
                with st.container():
                    c1, c2 = st.columns([4, 1])
                    with c1:
                        st.markdown(f"~~{t['description']}~~")
                        st.caption(f"Done on {pd.to_datetime(t.get('created_at', 0), unit='s').strftime('%Y-%m-%d')}")
                    with c2:
                        if st.button("Delete", key=f"del_c_{t['id']}"):
                            delete_task(t['id'])
                            st.rerun()

    # 3. Page Level Chat
    render_page_chat(
        "Task Management", 
        ManagerAgent(), 
        json.dumps(all_tasks, indent=2)
    )
