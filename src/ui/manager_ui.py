import streamlit as st
import asyncio
import random
import time
import json
from datetime import datetime
from agents.manager import ManagerAgent
from utils.recorder import WorkflowRecorder
from utils.voice_manager import VoiceManager
from automation_engine import AutomationEngine
from memory import Memory
from discovery_engine import DiscoveryEngine
from database import (
    create_chat_session, save_chat_message, get_chat_history, 
    get_chat_sessions, update_session_title, get_dashboard_stats
)
from src.ui.components import premium_header, confirm_action

# Force registration of nodes if needed
import src.nodes.domain.wordpress_node

def execute_tool_logic(tool, params, agent, recorder, voice, memory, discovery, engine, status_container):
    """
    Standardized execution logic for Manager tools.
    """
    try:
        from utils.agent_registry import get_agent_class
        from workflow import run_outreach
        from workflow_manager import save_workflow, extract_steps_from_workflow
        
        if tool == "run_search":
            recorder.log_step(tool, params, description=f"Search for '{params.get('query')}'")
            status_container.write(f"Offloading search for: {params.get('query')} to Mission Control...")
            
            strategy = {
                "strategy_name": f"Search: {params.get('query')}",
                "goal": params.get('query'),
                "mode": "conductor",
                "sequence": [{"type": "agent", "agent": "RESEARCHER", "task": params.get('query')}]
            }
            engine.start_mission(strategy, agent)
            st.success("Search task sent to Mission Control!")
            voice.speak("I've started the search in the background.")
            memory.add_feedback(tool, "Success", 5, "Offloaded search to engine")

        elif tool == "save_workflow":
            name = params.get("name", "untitled_workflow")
            steps = recorder.get_workflow()
            if steps:
                save_workflow(name, f"Workflow created by Manager", steps=steps)
                st.success(f"Workflow '{name}' saved.")
                recorder.clear()
                voice.speak(f"Workflow {name} saved.")
            else:
                st.warning("No steps to save yet.")

        elif tool == "run_workflow":
            name = params.get("name")
            status_container.write(f"Loading workflow: {name}...")
            steps = extract_steps_from_workflow(name)
            if steps:
                status_container.info(f"Executing {len(steps)} steps for workflow: {name}")
                for step in steps:
                    s_tool = step.get('tool')
                    s_params = step.get('params', {})
                    status_container.write(f"Step: {step.get('description', s_tool)}")
                    if s_tool == "run_search":
                        asyncio.run(run_outreach(s_params.get("query")))
                st.success("Workflow execution complete.")
                memory.add_feedback(tool, "Success", 5, f"Ran workflow {name}")
            else:
                st.error("Workflow not found or empty.")

        elif tool == "build_wordpress_site":
            goal = params.get("goal")
            domain = params.get("domain", "lookoverhere.xyz")
            directory = params.get("directory", "")
            status_container.write(f"Initiating WP Build: {domain}/{directory}...")
            
            sequence = [{"type": "agent", "agent": "WORDPRESS", "task": f"Install WP on {domain}/{directory}"}]
            strategy = {"strategy_name": f"WP Build: {domain}", "mode": "conductor", "goal": goal, "sequence": sequence}
            engine.start_mission(strategy, agent)
            st.success("Mission offloaded to Engine!")
            voice.speak("I've started the site build mission.")
            memory.add_feedback(tool, "Success", 5, "Offloaded WP build to engine")

        elif tool == "delegate_task":
            agent_name = params.get("agent_name")
            instructions = params.get("instructions")
            AgentClass = get_agent_class(agent_name)
            if AgentClass:
                sub_agent = AgentClass()
                status_container.write(f"Delegating to **{agent_name}**...")
                result = None
                if hasattr(sub_agent, 'think'): result = sub_agent.think(instructions)
                elif hasattr(sub_agent, 'run'): result = sub_agent.run(instructions)
                
                content_to_display = f"**Result from {agent_name}:**\n{result}"
                st.session_state['manager_messages'].append({"role": "assistant", "content": content_to_display})
                save_chat_message(st.session_state['current_session_id'], "assistant", content_to_display)
                st.info(content_to_display)
            else:
                st.error(f"Agent {agent_name} not found.")

        elif tool == "conductor_mission":
            goal = params.get("goal")
            sequence = params.get("sequence", [])
            status_container.info(f"🚀 Launching Conductor Mission: {goal}")
            strategy = {"strategy_name": f"Conductor: {goal[:30]}", "goal": goal, "mode": "conductor", "sequence": sequence}
            engine.start_mission(strategy, agent)
            st.success("Mission started! Check 'Mission Control'.")
            memory.add_feedback(tool, "Success", 5, f"Launched conductor for: {goal}")

        elif tool == "design_workflow":
            goal = params.get("goal")
            status_container.info(f"🎨 Designing Workflow: {goal}")
            result = agent.design_workflow(goal)
            if "error" in result: st.error(result['error'])
            else:
                content = f"✅ **Workflow Designed!**\n- **File:** `{result['file']}`"
                st.success(content)
                st.session_state['manager_messages'].append({"role": "assistant", "content": content})
                save_chat_message(st.session_state['current_session_id'], "assistant", content)

        elif tool == "execute_workflow":
            wf_name = params.get("workflow_name")
            status_container.info(f"🚀 Executing Workflow: {wf_name}")
            result = asyncio.run(agent.execute_workflow(wf_name, params.get("payload", {})))
            content = f"🚀 **Workflow Execution Started!** ID: {result.get('execution_id')}"
            st.success(content)
            st.session_state['manager_messages'].append({"role": "assistant", "content": content})
            save_chat_message(st.session_state['current_session_id'], "assistant", content)

    except Exception as e:
        st.error(f"Execution failed: {e}")
        voice.speak("I encountered an error.")

def render_manager_ui():
    premium_header("Manager Agent", "Your AI Operations Commander.")

    # Initialize Session State
    st.session_state['manager_agent'] = ManagerAgent()
    
    if 'staged_plans' not in st.session_state:
        st.session_state['staged_plans'] = []

    if 'workflow_recorder' not in st.session_state:
        st.session_state['workflow_recorder'] = WorkflowRecorder()
        
    # --- SESSION MANAGEMENT ---
    recent_sessions = get_chat_sessions(limit=15)
    
    if 'current_session_id' not in st.session_state:
        if recent_sessions:
            st.session_state['current_session_id'] = recent_sessions[0]['id']
        else:
            st.session_state['current_session_id'] = create_chat_session()
            
    current_history = get_chat_history(st.session_state['current_session_id'])
    st.session_state['manager_messages'] = current_history
    
    if not st.session_state['manager_messages']:
        welcome_msg = "How can I help you today?"
        st.session_state['manager_messages'].append({"role": "assistant", "content": welcome_msg})
        save_chat_message(st.session_state['current_session_id'], "assistant", welcome_msg)

    if 'voice_manager' not in st.session_state:
        vm = VoiceManager()
        vm.start_listening()
        st.session_state['voice_manager'] = vm

    if 'memory_system' not in st.session_state:
        st.session_state['memory_system'] = Memory()

    if 'discovery_engine' not in st.session_state:
        st.session_state['discovery_engine'] = DiscoveryEngine()

    agent = st.session_state['manager_agent']
    recorder = st.session_state['workflow_recorder']
    voice = st.session_state['voice_manager']
    memory = st.session_state['memory_system']
    discovery = st.session_state['discovery_engine']

    # --- SIDEBAR ---
    with st.sidebar:
        st.title("🤖 Manager Access")
        
        # STOP ALL
        if st.button("🚨 EMERGENCY: STOP ALL", type="primary", use_container_width=True):
             if 'automation_engine' in st.session_state:
                 st.session_state['automation_engine'].stop()
             st.error("All engines stopped.")
             st.rerun()

        st.divider()

        # Mission Status
        if 'automation_engine' in st.session_state:
            engine = st.session_state['automation_engine']
            if engine.is_running:
                st.success(f"🚀 **Mission Running**\n\n'{engine.current_mission}'")
                if st.button("Stop Mission"):
                    engine.stop()
                    st.rerun()
            else:
                st.caption("System Status: Idle ⚪")
        
        st.divider()

        # Log Viewer
        with st.expander("📜 Logs", expanded=False):
            if 'automation_engine' in st.session_state and st.session_state['automation_engine'].logs:
                for log in reversed(st.session_state['automation_engine'].logs[-20:]):
                    st.caption(f"_{log}_")
            else:
                st.caption("No logs.")

        st.divider()
        
        # New Chat
        if st.button("➕ Start New Chat"):
            new_id = create_chat_session()
            st.session_state['current_session_id'] = new_id
            st.session_state['manager_messages'] = []
            st.session_state['transcript_log'] = []
            st.rerun()

        # Session Switcher
        if recent_sessions:
            session_options = {s['id']: f"{s['title'] or 'New Chat'} ({datetime.fromtimestamp(s['created_at']).strftime('%H:%M')})" for s in recent_sessions}
            selected_session_id = st.selectbox(
                "Recent Chats", 
                options=recent_sessions, 
                format_func=lambda s: f"{s['title'] or 'New Chat'} ({datetime.fromtimestamp(s['created_at']).strftime('%m/%d %H:%M')})",
                index=0,
                key="session_selector"
            )
            
            if selected_session_id['id'] != st.session_state['current_session_id']:
                 st.session_state['current_session_id'] = selected_session_id['id']
                 st.rerun()
                 
    # --- MAIN UI TABS ---
    tab_dash, tab_chat, tab_exec = st.tabs(["📊 Dashboard", "💬 Discussion", "🚀 Execution"])

    # --- TAB 1: DASHBOARD ---
    with tab_dash:
        st.subheader("Global Operations Dashboard")
        
        try:
            stats = get_dashboard_stats()
        except:
            stats = {"leads_total": 0, "active_campaigns": 0, "system_health": "Unknown"}
            
        col1, col2, col3 = st.columns(3)
        col1.metric("System Health", stats.get('system_health', 'Operational'), delta="Normal")
        col2.metric("Total Leads", stats.get('leads_total', 0))
        col3.metric("Active Campaigns", stats.get('active_campaigns', 0)) # Placeholder if not implemented in DB
        
        st.divider()
        st.subheader("Recent Activity")
        if 'transcript_log' in st.session_state and st.session_state['transcript_log']:
            for line in reversed(st.session_state['transcript_log'][-5:]):
                 st.caption(f"> {line}")
        else:
            st.info("No recent voice/activity logs.")

    # --- TAB 2: CHAT ---
    with tab_chat:
        chat_container = st.container(height=500)
        with chat_container:
             for msg in st.session_state['manager_messages']:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                    
                    if msg.get("tool_call") and msg["tool_call"] not in ["chat"]:
                        tool = msg["tool_call"]
                        params = msg.get("tool_params", {})
                        
                        stageable_tools = ["conductor_mission", "design_workflow", "build_wordpress_site", "execute_workflow"]
                        if tool in stageable_tools:
                            if st.button("📥 Stage", key=f"stage_{msg.get('id', random.randint(0, 100000))}"):
                                st.session_state['staged_plans'].append({
                                    "id": f"plan_{len(st.session_state['staged_plans'])+1}",
                                    "tool": tool,
                                    "params": params,
                                    "name": f"{tool} Plan ({datetime.now().strftime('%H:%M')})"
                                })
                                st.toast("Plan added to Execution tab!")
                                
        # Chat Input
        user_input = st.chat_input("What should we do?")
        
        final_prompt = user_input
        # Voice integration
        voice_command = None
        while True:
            event = voice.get_latest_event()
            if not event: break
            if event['type'] == 'command':
                voice_command = event['payload']
                st.session_state['transcript_log'].append(f"Command: {voice_command}")
                st.toast(f"Voice Command: {voice_command}")
            elif event['type'] == 'transcription':
                text = event['payload']
                st.session_state['transcript_log'].append(f"{text}")
                # We could auto-submit if confident, but safe to just log for now unless keyword
        
        if voice_command:
            final_prompt = voice_command

        if final_prompt:
            with chat_container:
                st.session_state['manager_messages'].append({"role": "user", "content": final_prompt})
            save_chat_message(st.session_state['current_session_id'], "user", final_prompt)
            
            if len(st.session_state['manager_messages']) <= 2: 
                update_session_title(st.session_state['current_session_id'], final_prompt[:50])

            with st.chat_message("user"):
                st.markdown(final_prompt)

            with st.chat_message("assistant"):
                with st.spinner("Manager is thinking..."):
                    response_json = agent.think(final_prompt, intent_history=st.session_state['manager_messages'][-5:])
                    if not response_json: response_json = {"tool": "chat", "reply": "I'm sorry, I encountered an error."}
                    if isinstance(response_json, list): response_json = response_json[0] if response_json else {"tool": "chat", "reply": "Empty response."}
                    
                    tool = response_json.get("tool")
                    params = response_json.get("params", {})
                    reply = response_json.get("reply", "Processing request...")

                display_content = f"{reply}\n\n🔧 **Tool Call Detected:** `{tool}`" if tool and tool != "chat" else reply
                st.markdown(display_content)
                
                st.session_state['manager_messages'].append({
                    "role": "assistant", "content": display_content, "tool_call": tool, "tool_params": params
                })
                save_chat_message(st.session_state['current_session_id'], "assistant", display_content, tool_call=tool, tool_params=params)
                
                voice.speak(reply)

                if tool and tool != "chat":
                    with st.status(f"⚡ Working: {tool}...", expanded=False) as status:
                        execute_tool_logic(tool, params, agent, recorder, voice, memory, discovery, engine, status)
                        status.update(label="Task Complete", state="complete")
                    st.rerun()

    # --- TAB 3: EXECUTION ---
    with tab_exec:
        st.subheader("🚀 Execution Staging Area")
        if not st.session_state['staged_plans']:
            st.info("No plans staged yet.")
        else:
            for i, plan in enumerate(st.session_state['staged_plans']):
                with st.expander(f"📋 {plan['name']}", expanded=True):
                    st.json(plan['params'])
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        if st.button("▶️ Run", key=f"run_staged_{i}"):
                            st.session_state['active_execution_plan'] = plan
                            st.rerun()
                    with c2:
                        if st.button("🗑️ Clear", key=f"clear_staged_{i}"):
                            st.session_state['staged_plans'].pop(i)
                            st.rerun()

    # --- TRAP EXECUTION ---
    if 'active_execution_plan' in st.session_state and st.session_state['active_execution_plan']:
        plan = st.session_state.pop('active_execution_plan')
        with tab_exec:
             with st.status(f"Executing {plan['tool']}...", expanded=True) as status:
                execute_tool_logic(plan['tool'], plan['params'], agent, recorder, voice, memory, discovery, engine, status)
                status.update(label="Staged Task Complete", state="complete")
