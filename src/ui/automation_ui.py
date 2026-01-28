import streamlit as st
import time
import json
from workflow_manager import list_workflows, load_workflow, save_workflow, delete_workflow
from agents import ManagerAgent
from ui.manager_ui import render_manager_ui

def render_automation_hub():
    """Renders the Automation Hub UI component."""
    st.header("🤖 Automation Hub")
    st.caption("Autonomous mission control center. Monitor and manage long-running agent loops.")
    
    tab_manager, tab_status = st.tabs(["💬 AI Manager", "📊 Mission Control"])
    
    with tab_manager:
         render_manager_ui()

    with tab_status:
        if 'automation_engine' not in st.session_state:
            st.error("Automation Engine not initialized.")
            return
            
        engine = st.session_state['automation_engine']
        
        # Stats Row
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Status", "Running 🟢" if engine.is_running else "Idle ⚪")
        c2.metric("Missions Run", engine.stats['missions_total'])
        c3.metric("Leads Found", engine.stats['leads_found'])
        c4.metric("Emails Sent", engine.stats['emails_sent'])
        
        st.divider()
        
        col_main, col_logs = st.columns([2, 1])
        
        with col_main:
            st.subheader("Mission Control")
            
            # --- NEW: TABBED VIEW FOR STRATEGY VS TASK ---
            mc_tabs = st.tabs(["🚀 Strategic Missions", "⚡ Task Automation"])
            
            with mc_tabs[0]:
                st.caption("Execute long-running, multi-agent strategies.")
                # Pending Strategy Loader
                if 'pending_strategy' in st.session_state:
                    strat = st.session_state['pending_strategy']
                    st.info(f"Loaded Strategy: **{strat.get('strategy_name', 'Unnamed')}**")
                    
                    if st.button("🚀 Launch Autonomous Mission", type="primary", disabled=engine.is_running):
                        # Start the engine
                        manager = ManagerAgent() # Create a fresh instance
                        engine.start_mission(strat, manager)
                        del st.session_state['pending_strategy'] # Clear pending
                        st.rerun()
                elif not engine.is_running:
                    st.info("No strategy loaded. Go to Strategy Laboratory to generate one.")

            with mc_tabs[1]:
                st.caption("Run specific, deterministic standard operating procedures (SOPs).")
                
                tasks = list_workflows(type_filter="task")
                if not tasks:
                    st.info("No 'Task' workflows found. Create one in Workflow Builder with 'type: task'.")
                else:
                    selected_task = st.selectbox("Select Task / SOP", tasks)
                    if st.button("▶️ Run Task", disabled=engine.is_running):
                        # Adapt the task execution effectively
                        # Ideally we create a temporary strategy wrapper
                        task_data = load_workflow(selected_task)
                        
                        temp_strat = {
                            "strategy_name": f"Task: {selected_task}",
                            "mode": "conductor",
                            "sequence": [{"type": "workflow", "name": selected_task}],
                            "goal": f"Execute task {selected_task}"
                        }
                        
                        manager = ManagerAgent()
                        engine.start_mission(temp_strat, manager)
                        st.rerun()
            
            if engine.is_running:
                st.markdown(f"**Current Mission:** {engine.current_mission}")
                if st.button("🛑 STOP AUTOMATION", type="secondary"):
                    engine.stop()
                    st.rerun()
                    
                st.success("Automation is running in the background. You can navigate away, but do not close the tab.")

        with col_logs:
            st.subheader("Live Logs")
            # Auto-refresh mechanism
            col_ref1, col_ref2 = st.columns([1, 1])
            with col_ref1:
                if st.button("🔄 Refresh Now"):
                    st.rerun()
            with col_ref2:
                auto_ref = st.toggle("Auto-Live", value=engine.is_running, key="log_autorefresh")
            
            log_container = st.container(height=400)
            if engine.logs:
                log_text = "\n".join(engine.logs[::-1]) # Reverse order
                log_container.code(log_text, language="text")
            else:
                log_container.write("No logs yet.")
            
            # Trigger rerun if auto-refresh is on and engine is running
            if auto_ref and engine.is_running:
                 time.sleep(2)
                 st.rerun()

def render_workflow_builder():
    """Renders the Workflow Builder UI component."""
    st.header("🛠️ Workflow Builder")
    st.caption("Design custom agent workflows using markdown.")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.subheader("My Workflows")
        workflows = list_workflows()
        
        # Action: Content Creator
        if st.button("➕ New Workflow", width="stretch"):
            st.session_state['editing_workflow'] = None
            st.session_state['workflow_name'] = ""
            st.session_state['workflow_desc'] = ""
            st.session_state['workflow_content'] = ""
            st.rerun()

        for wf in workflows:
            if st.button(f"📄 {wf}", key=f"sel_{wf}", width="stretch"):
                data = load_workflow(wf)
                if data:
                    st.session_state['editing_workflow'] = wf
                    st.session_state['workflow_name'] = wf
                    st.session_state['workflow_desc'] = data['description']
                    st.session_state['workflow_content'] = data['content']
                    st.rerun()
                    
    with col2:
        st.subheader("Editor")
        
        with st.form("workflow_editor_form"):
            w_name = st.text_input("Filename (e.g. my_workflow.md)", value=st.session_state.get('workflow_name', ''))
            w_desc = st.text_input("Description", value=st.session_state.get('workflow_desc', ''))
            w_content = st.text_area("Workflow Steps (Markdown)", value=st.session_state.get('workflow_content', ''), height=400)
            
            c_save, c_del = st.columns([4, 1])
            
            with c_save:
                if st.form_submit_button("💾 Save Workflow", type="primary", width="stretch"):
                    if w_name and w_content:
                        save_workflow(w_name, w_content, w_desc)
                        st.success(f"Saved {w_name}!")
                        st.session_state['editing_workflow'] = w_name
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Name and Content are required.")
                        
            with c_del:
                delete_submitted = st.form_submit_button("🗑️ Delete", type="secondary", width="stretch", disabled=not bool(st.session_state.get('editing_workflow')))
                
                if delete_submitted and st.session_state.get('editing_workflow'):
                    delete_workflow(st.session_state['editing_workflow'])
                    st.success("Deleted.")
                    st.session_state['editing_workflow'] = None
                    st.session_state['workflow_name'] = ""
                    st.session_state['workflow_desc'] = ""
                    st.session_state['workflow_content'] = ""
                    time.sleep(1)
                    st.rerun()
