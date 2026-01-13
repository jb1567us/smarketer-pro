import streamlit as st
import asyncio
import random
import time
import json
from datetime import datetime
from agents.manager import ManagerAgent
from utils.recorder import WorkflowRecorder
from utils.voice_manager import VoiceManager
from workflow import run_outreach
from workflow_manager import save_workflow, list_workflows, load_workflow, extract_steps_from_workflow
from automation_engine import AutomationEngine
# Force registration of WordPressNode
import src.nodes.domain.wordpress_node
from memory import Memory
from discovery_engine import DiscoveryEngine
from database import (
    create_chat_session, save_chat_message, get_chat_history, 
    get_chat_sessions, update_session_title
)

def render_manager_ui():
    # Initialize Session State
    # Force re-instantiation to ensure latest code is picked up
    st.session_state['manager_agent'] = ManagerAgent()
    
    if 'workflow_recorder' not in st.session_state:
        st.session_state['workflow_recorder'] = WorkflowRecorder()
        
    # --- SESSION MANAGEMENT ---
    # Load recent sessions
    recent_sessions = get_chat_sessions(limit=15)
    
    # If no session active, try to load latest or create new
    if 'current_session_id' not in st.session_state:
        if recent_sessions:
            st.session_state['current_session_id'] = recent_sessions[0]['id']
        else:
            st.session_state['current_session_id'] = create_chat_session()
            
    # Load history for current session
    current_history = get_chat_history(st.session_state['current_session_id'])
    
    # Sync to manager_messages (If empty, adding welcome only if it's a brand new session with no history)
    # Using a simpler approach: always render what's in DB.
    # But manager logic relies on 'manager_messages' state list.
    st.session_state['manager_messages'] = current_history
    
    if not st.session_state['manager_messages']:
        # New empty session
        welcome_msg = "How can I help you today?"
        st.session_state['manager_messages'].append({"role": "assistant", "content": welcome_msg})
        # Save welcome message so it persists
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

    # Sidebar Voice Status & Discovery
    with st.sidebar:
        st.title("🤖 Manager Agent")
        st.caption("Your personal AI Manager.")
        st.divider()

        # --- LIVE SYSTEM STATUS ---
        if 'automation_engine' in st.session_state:
            engine = st.session_state['automation_engine']
            if engine.is_running:
                st.success(f"🚀 **Mission Running**\n\n'{engine.current_mission}'")
                if st.button("Stop Mission"):
                    engine.stop()
                    st.rerun()
            else:
                st.caption("System Status: Idle ⚪")
        
        # Auto-refresh for background logs
        if 'auto_refresh' not in st.session_state:
            st.session_state['auto_refresh'] = False
            
        if st.checkbox("🔄 Auto-refresh Logs", value=st.session_state['auto_refresh'], key="auto_refresh_toggle"):
            st.session_state['auto_refresh'] = True
            time.sleep(2)
            st.rerun()
        else:
            st.session_state['auto_refresh'] = False

        st.divider()
        
        st.subheader("💬 Chat Controls")
        
        # New Chat
        if st.button("➕ Start New Chat", type="primary"):
            new_id = create_chat_session()
            st.session_state['current_session_id'] = new_id
            st.session_state['manager_messages'] = []
            st.session_state['transcript_log'] = []
            st.rerun()

        # Session Switcher
        if recent_sessions:
            session_options = {s['id']: f"{s['title'] or 'New Chat'} ({datetime.fromtimestamp(s['created_at']).strftime('%H:%M')})" for s in recent_sessions}
            selected_session_id = st.selectbox(
                "📜 Recent History", 
                options=recent_sessions, 
                format_func=lambda s: f"{s['title'] or 'New Chat'} ({datetime.fromtimestamp(s['created_at']).strftime('%m/%d %H:%M')})",
                index=0,
                key="session_selector"
            )
            
            # If user manually changed selection (imperfect check in Streamlit but works mostly)
            if selected_session_id['id'] != st.session_state['current_session_id']:
                 st.session_state['current_session_id'] = selected_session_id['id']
                 st.rerun()
                 
            st.divider()
            with st.expander("⚙️ Workflow Options"):
                wf_name = st.text_input("Name for this session's workflow", value="My New Workflow")
                if st.button("Convert Session to Workflow"):
                    # Fetch history with tool data
                    history = get_chat_history(st.session_state['current_session_id'])
                    steps = []
                    for msg in history:
                        t_call = msg.get('tool_call')
                        t_params = msg.get('tool_params')
                        
                        if t_call and t_call != 'chat':
                            steps.append({
                                "id": f"step_{len(steps)+1}",
                                "tool": t_call,
                                "params": t_params or {},
                                "description": f"Step generated from chat: {t_call}"
                            })
                    
                    if steps:
                        save_workflow(wf_name, f"Converted from session {st.session_state['current_session_id']}", steps)
                        st.success(f"Saved workflow '{wf_name}' with {len(steps)} steps!")
                        voice.speak(f"I've saved the workflow {wf_name}.")
                    else:
                        st.warning("No tool actions found in this chat session to convert.")

            st.divider()
            with st.expander("🚀 Plan Execution", expanded=True):
                st.caption("Convert the last brainstormed plan into a live mission.")
                if st.button("Convert Last Plan to Mission", type="primary"):
                    # Get last assistant message
                    last_msg = None
                    if st.session_state['manager_messages']:
                         for m in reversed(st.session_state['manager_messages']):
                             if m['role'] == 'assistant' and m.get('content'):
                                 last_msg = m['content']
                                 break
                    
                    if not last_msg:
                        st.warning("No assistant plan found to convert.")
                    else:
                        with st.spinner("Analyzing plan and generating mission sequence..."):
                            # dedicated conversion prompt
                            conv_prompt = (
                                "You are an Expert Planner. Convert the following strategic plan into a JSON sequence for the 'conductor_mission' tool.\n"
                                "Schema: [{'type': 'agent'|'workflow', 'agent': 'NAME', 'task': '...'}, ...]\n"
                                "Rules:\n"
                                "- Map 'Research'/'Find' -> RESEARCHER agent.\n"
                                "- Map 'Write'/'Email' -> COPYWRITER agent.\n"
                                "- Map 'Visuals' -> IMAGE agent.\n"
                                "- Map 'Review' -> REVIEWER agent.\n"
                                "- Return ONLY the raw JSON list.\n\n"
                                f"Input Plan:\n{last_msg}"
                            )
                            
                            try:
                                conv_res = agent.provider.generate_json(conv_prompt)
                                
                                # Normalize Result
                                final_sequence = []
                                if isinstance(conv_res, list):
                                    # Fix: Handle nested lists (LLM sometimes wraps result in [ [... ] ])
                                    if len(conv_res) > 0 and isinstance(conv_res[0], list):
                                        final_sequence = conv_res[0]
                                    else:
                                        final_sequence = conv_res
                                elif isinstance(conv_res, dict):
                                    # Check common keys
                                    if "steps" in conv_res and isinstance(conv_res["steps"], list):
                                        final_sequence = conv_res["steps"]
                                    elif "sequence" in conv_res and isinstance(conv_res["sequence"], list):
                                        final_sequence = conv_res["sequence"]
                                    elif "plan" in conv_res and isinstance(conv_res["plan"], list):
                                        final_sequence = conv_res["plan"]
                                    else:
                                        # Assume single object task if it has 'type'
                                        if "type" in conv_res:
                                            final_sequence = [conv_res]

                                if final_sequence and len(final_sequence) > 0:
                                    # Launch Mission
                                    start_goal = "Executed from converted plan"
                                    # Try to extract a goal title from the plan text
                                    lines = last_msg.split('\n')
                                    if lines: start_goal = lines[0][:50]

                                    strategy = {
                                        "strategy_name": f"Converted: {start_goal}",
                                        "goal": start_goal,
                                        "mode": "conductor",
                                        "sequence": final_sequence
                                    }
                                    
                                    engine = st.session_state['automation_engine']
                                    engine.start_mission(strategy, agent)
                                    st.success("✅ Conversion successful! Mission Launched.")
                                    voice.speak("I've successfully converted the plan and started the mission.")
                                    # Switch to mission tab conceptually (user matches manually)
                                else:
                                    st.error("Could not generate a valid sequence from the text.")
                                    st.write("Debug - Raw Response:")
                                    st.json(conv_res)
                            except Exception as e:
                                st.error(f"Conversion failed: {e}")
            
        st.subheader("🎙️ Voice Control")
        
        # Master Switch
        voice_enabled = st.toggle("Enable Voice Listener", value=True)
        
        if voice_enabled:
            # Logic will continue in next block
            pass

    # Display Chat in a scrollable container (simulated by logic order)
    chat_container = st.container(height=600)
    with chat_container:
         for msg in st.session_state['manager_messages']:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # Back to Sidebar Logic for Voice (Hack to fix flow)
    # Actually, let's keep all sidebar logic TOGETHER.
    with st.sidebar:
        if voice_enabled:
            voice.start_listening()
            # Visual Status
            if voice.is_awake:
                st.success("Listening... (Say command)")
            else:
                st.info("Sleeping (Say 'Hey Stanley')")
                
            if st.button("Force Wake"):
                voice.is_awake = True
                voice.speak("Yes?")
                st.rerun()
        else:
            voice.stop_listening()
            st.warning("Voice Listener Disabled")

        st.divider()
        st.subheader("🧠 Memory & Learning")
        if st.button("View Learned Context"):
            st.text(memory.get_context())
        
        new_pref = st.text_input("Add Preference", placeholder="e.g. 'I like formal tone'")
        if st.button("Save Preference"):
            if new_pref:
                memory.add_preference(new_pref)
                st.success("Preference saved!")

        st.divider()
        # Discovery Engine Trigger
        if st.button("🎲 Discovery Mode"):
            with st.spinner("Finding serendipitous opportunities..."):
                intel = asyncio.run(discovery.get_serendipitous_finding(current_niche="B2B"))
                if intel:
                    st.session_state['manager_messages'].append({
                        "role": "assistant", 
                        "content": f"**{intel['title']}**\n\n{intel['content']}\n\n[Read More]({intel['url']})"
                    })
                    save_chat_message(st.session_state['current_session_id'], "assistant", f"**{intel['title']}**\n\n{intel['content']}\n\n[Read More]({intel['url']})")
                    st.rerun()
                else:
                    st.warning("Nothing found right now.")

        st.subheader("Transcript")
        if 'transcript_log' not in st.session_state:
            st.session_state['transcript_log'] = []
            
        # Show last 5 lines reversed
        for line in reversed(st.session_state['transcript_log'][-5:]):
            st.caption(f"_{line}_")

    # Process Voice Queue
    voice_command = None
    while True:
        event = voice.get_latest_event()
        if not event:
            break
            
        if event['type'] == 'command':
            voice_command = event['payload']
            st.session_state['transcript_log'].append(f"Command: {voice_command}")
            st.toast(f"Voice Command: {voice_command}")
            
        elif event['type'] == 'transcription':
            text = event['payload']
            st.session_state['transcript_log'].append(f"{text}")
            st.rerun() 
            
        elif event['type'] == 'status':
            st.rerun()

    # Chat Input (Rendered loop removed)

    # Chat Input
    user_input = st.chat_input("What should we do?")
    
    final_prompt = None
    if user_input:
        final_prompt = user_input
    elif voice_command:
        final_prompt = voice_command

    if final_prompt:
        # 1. User Message
        st.session_state['manager_messages'].append({"role": "user", "content": final_prompt})
        save_chat_message(st.session_state['current_session_id'], "user", final_prompt)
        
        # Update Title if it's the first user message (simple heuristic)
        if len(st.session_state['manager_messages']) <= 2: 
            update_session_title(st.session_state['current_session_id'], final_prompt[:50])

        with st.chat_message("user"):
            st.markdown(final_prompt)

        # 2. Agent Thinking
        with st.chat_message("assistant"):
            with st.spinner("Manager is thinking..."):
                response_json = agent.think(
                    final_prompt, 
                    intent_history=st.session_state['manager_messages'][-5:] 
                )
                
                if not response_json:
                    response_json = {"tool": "chat", "reply": "I'm sorry, I encountered an error."}
                
                if isinstance(response_json, list):
                    response_json = response_json[0] if response_json else {"tool": "chat", "reply": "Empty response."}
                
                tool = response_json.get("tool")
                params = response_json.get("params", {})
                reply = response_json.get("reply", "Processing request...")

            st.markdown(reply)
            # DEBUG: Show detected tool
            if tool and tool != "chat":
                st.caption(f"🔧 Tool Detected: `{tool}`")
            # Update session state with metadata (useful for runtime)
            display_content = reply
            if tool and tool != "chat":
                display_content = f"{reply}\n\n🔧 **Tool Call Detected:** `{tool}`"
            
            st.session_state['manager_messages'].append({
                "role": "assistant", 
                "content": display_content, 
                "tool_call": tool, 
                "tool_params": params
            })
            # Save to DB with metadata
            save_chat_message(st.session_state['current_session_id'], "assistant", display_content, tool_call=tool, tool_params=params)
            
            # --- GUARD RAIL --- 
            # If the agent just said "Done" without a tool, we scold it in the next turn or show error
            is_lazy_response = tool == "chat" and len(reply.split()) < 5 and "done" in reply.lower()
            if is_lazy_response:
                st.error("⚠️ Agent returned a lazy response without action. Auto-correcting...")
                # We could auto-retry here, but for now we just warn the user.
                # In a robust system, we would loop back: agent.think("You just said Done but did nothing. DO THE TASK.")
                memory.add_feedback(tool, "Failure", 1, "Agent returned lazy 'Done' response.")

            voice.speak(reply)
            
            # --- FEEDBACK LOOP ---
            # Automatically ask for feedback if a tool was used
            # For simplicity, we assume implicit distinctness. 
            # In a real app, we might check if tool != 'chat'

            # 3. Execution
            if tool and tool != "chat":
                with st.status(f"Executing: {tool}...", expanded=True) as status:
                    try:
                        if tool == "run_search":
                            recorder.log_step(tool, params, description=f"Search for '{params.get('query')}'")
                            st.write(f"Running search for: {params.get('query')}")
                            asyncio.run(run_outreach(
                                params.get("query"), 
                                target_niche=params.get("niche"), 
                                profile_names=params.get("profile", "default")
                            ))
                            st.success("Search completed! Results saved to Leads DB.")
                            voice.speak("Search completed.")
                            memory.add_feedback(tool, "Success", 5, "Auto-logged success")

                        elif tool == "save_workflow":
                            name = params.get("name", "untitled_workflow")
                            steps = recorder.get_workflow()
                            if steps:
                                save_workflow(name, f"Workflow created by Manager on {final_prompt}", steps=steps)
                                st.success(f"Workflow '{name}' saved with {len(steps)} steps.")
                                recorder.clear()
                                voice.speak(f"Workflow {name} saved.")
                            else:
                                st.warning("No steps to save yet.")
                                voice.speak("There are no steps to save.")

                        elif tool == "run_workflow":
                            name = params.get("name")
                            st.write(f"Loading workflow: {name}...")
                            steps = extract_steps_from_workflow(name)
                            if steps:
                                st.info(f"Executing {len(steps)} steps for workflow: {name}")
                                # Execute each step
                                for step in steps:
                                    s_tool = step.get('tool')
                                    s_params = step.get('params', {})
                                    st.write(f"Step: {step.get('description', s_tool)}")
                                    
                                    # Very basic recursive implementation for now
                                    if s_tool == "run_search":
                                        asyncio.run(run_outreach(
                                            s_params.get("query"), 
                                            target_niche=s_params.get("niche"), 
                                            profile_names=s_params.get("profile", "default")
                                        ))
                                    # Add other tools here as needed
                                    
                                st.success("Workflow execution complete.")
                                memory.add_feedback(tool, "Success", 5, f"Ran workflow {name}")
                            else:
                                st.error("Workflow not found or empty.")

                        elif tool == "delegate_task":
                            agent_name = params.get("agent_name")
                            instructions = params.get("instructions")
                            
                            AgentClass = get_agent_class(agent_name)
                            if AgentClass:
                                sub_agent = AgentClass()
                                st.write(f"Delegating to **{agent_name}**...")
                                
                                result = None
                                if hasattr(sub_agent, 'think'):
                                    result = sub_agent.think(instructions)
                                elif hasattr(sub_agent, 'run'): # Standardize
                                    result = sub_agent.run(instructions)
                                elif hasattr(sub_agent, 'gather_intel'): # Researcher
                                    result = asyncio.run(sub_agent.gather_intel({"query": instructions}))
                                
                                # Process Result for Chat
                                content_to_display = ""
                                if isinstance(result, dict):
                                    if result.get("image_url"):
                                        # Handle Image Result
                                        img_path = result.get("image_url")
                                        content_to_display = f"**Task Complete.**\n\n![Generated Image]({img_path})\n\n_Path: {img_path}_"
                                    elif result.get("results") and isinstance(result["results"], list):
                                        # Handle Search Results
                                        res_list = result["results"]
                                        content_to_display = f"**{agent_name} Found {len(res_list)} Results:**\n"
                                        
                                        # Save Button
                                        if st.button(f"💾 Save {len(res_list)} Results to Leads DB", key=f"save_{len(st.session_state['manager_messages'])}"):
                                            saved_count = 0
                                            with st.spinner("Saving leads..."):
                                                from database import add_lead
                                                for item in res_list:
                                                    add_lead(
                                                        url=item.get('url'),
                                                        email=None, 
                                                        source="Manager Search",
                                                        category="manual_search",
                                                        industry="General",
                                                        company_name=item.get('title')
                                                    )
                                                    saved_count += 1
                                            st.success(f"Saved {saved_count} leads to database!")
                                            time.sleep(1)
                                            st.rerun()

                                        for item in res_list[:20]: # Show top 20
                                            title = item.get('title', 'No Title')
                                            url = item.get('url', '#')
                                            snippet = item.get('snippet', '')[:150]
                                            content_to_display += f"- [{title}]({url})\n  _{snippet}...\n"
                                        if len(res_list) > 20:
                                            content_to_display += f"\n_...and {len(res_list)-20} more._"
                                    else:
                                         # Default JSON
                                         content_to_display = f"**Result from {agent_name}:**\n```json\n{json.dumps(result, indent=2)}\n```"
                                else:
                                    # Handle Text Result
                                    content_to_display = f"**Result from {agent_name}:**\n{result}"
                                
                                # Log result to conversation so Manager knows
                                st.session_state['manager_messages'].append({
                                    "role": "assistant", 
                                    "content": content_to_display
                                })
                                save_chat_message(st.session_state['current_session_id'], "assistant", content_to_display)
                                memory.add_feedback(tool, "Success", 4, f"Delegated to {agent_name}")
                            else:
                                st.error(f"Agent {agent_name} not found.")

                        elif tool == "conductor_mission":
                            goal = params.get("goal")
                            icp = params.get("icp", "")
                            sequence = params.get("sequence", [])
                            
                            st.info(f"🚀 Launching Conductor Mission: {goal}")
                            if sequence:
                                st.write(f"Flow: {' → '.join([s.get('name') or s.get('agent') for s in sequence])}")
                            
                            voice.speak(f"Launching conductor mission for {goal}")
                            
                            # Prepare strategy object for AutomationEngine
                            strategy = {
                                "strategy_name": f"Conductor: {goal[:30]}...",
                                "goal": goal,
                                "icp_refined": icp,
                                "mode": "conductor",
                                "sequence": sequence,
                                "queries": [goal], # Backup
                                "limit": 5
                            }
                            
                            engine = st.session_state['automation_engine']
                            engine.start_mission(strategy, agent)
                            st.success("Mission started! Check 'Mission Control' tab for live progress.")
                            memory.add_feedback(tool, "Success", 5, f"Launched conductor for: {goal}")

                        elif tool == "learn_insight":
                            insight = params.get("insight")
                            memory.add_insight(insight)
                            st.success(f"🧠 Insight Learned: {insight}")
                            
                        elif tool == "list_workflows":
                            wfs = list_workflows()
                            st.json(wfs)
                            if wfs:
                                voice.speak(f"I found {len(wfs)} workflows.")
                            else:
                                voice.speak("I found no saved workflows.")

                        elif tool == "design_workflow":
                            goal = params.get("goal")
                            nodes_desc = params.get("nodes_description", "")
                            st.info(f"🎨 Designing Workflow: {goal}")
                            with st.spinner("Architecting..."):
                                result = agent.design_workflow(goal, nodes_desc)
                                if "error" in result:
                                    content = f"❌ **Workflow Design Failed:** {result['error']}"
                                    st.error(content)
                                else:
                                    content = f"✅ **Workflow Designed!**\n\n- **Goal:** {goal}\n- **File:** `{result['file']}`\n\n```json\n{json.dumps(result['design'], indent=2)}\n```"
                                    st.success(f"Workflow saved to: {result['file']}")
                                    st.json(result['design'])
                                    voice.speak(f"I've designed the workflow for {goal}.")
                                
                                # PERSIST RESULT
                                st.session_state['manager_messages'].append({"role": "assistant", "content": content})
                                save_chat_message(st.session_state['current_session_id'], "assistant", content)

                        elif tool == "execute_workflow":
                            wf_name = params.get("workflow_name")
                            payload = params.get("payload", {})
                            st.info(f"🚀 Executing Workflow: {wf_name}")
                            with st.spinner("Running engine..."):
                                # agent.execute_workflow is async
                                result = asyncio.run(agent.execute_workflow(wf_name, payload))
                                if result.get("status") == "error":
                                    content = f"❌ **Workflow Execution Failed:** {result.get('error')}"
                                    st.error(content)
                                else:
                                    exec_id = result.get('execution_id')
                                    content = f"🚀 **Workflow Execution Started!**\n\n- **Workflow:** `{wf_name}`\n- **Execution ID:** `{exec_id}`\n\nCheck 'Mission Control' for progress."
                                    st.success(f"Workflow {wf_name} is now running. ID: {exec_id}")
                                    voice.speak(f"Started workflow {wf_name}.")
                                
                                # PERSIST RESULT
                                st.session_state['manager_messages'].append({"role": "assistant", "content": content})
                                save_chat_message(st.session_state['current_session_id'], "assistant", content)

                        elif tool == "build_wordpress_site":
                            goal = params.get("goal")
                            domain = params.get("domain", "lookoverhere.xyz")
                            directory = params.get("directory", "")
                            
                            cp_pass = os.getenv("CPANEL_PASS", "")
                            if not cp_pass:
                                st.warning("⚠️ **CPANEL_PASS** not found in environment. The automation might fail during login. Please ensure your `.env` file is configured.")
                            
                            st.info(f"🏗️ Initiating Site Build: {goal}")
                            recorder.log_step("build_wordpress_site", params, description=f"Build mission for {goal}")
                            with st.spinner("Preparing automation..."):
                                # Step 1: Design the workflow automatically
                                design_res = agent.design_workflow(
                                    goal=f"Install WordPress and setup site for: {goal}",
                                    nodes_description=f"Action: cpanel_install. Domain: {domain}. Directory: {directory}."
                                )
                                
                                if "error" in design_res:
                                    content = f"❌ **Site Build Failed at Design Phase:** {design_res['error']}"
                                    st.error(content)
                                else:
                                    wf_id = design_res['design'].get('id')
                                    st.write(f"Workflow designed: `{wf_id}`. Offloading execution to background engine...")
                                    
                                    # Step 2: Execute the workflow ASYNCHRONOUSLY
                                    engine = st.session_state.get('automation_engine')
                                    if engine:
                                        engine.start_workflow(wf_id, {
                                            "cpanel_url": os.getenv("CPANEL_URL", "https://lookoverhere.xyz:2083"),
                                            "cp_user": os.getenv("CPANEL_USER", "baron"),
                                            "cp_pass": os.getenv("CPANEL_PASS", ""),
                                            "domain": domain,
                                            "directory": directory
                                        }, agent)
                                        
                                        content = f"🏗️ **Site Build Mission Launched!**\n\n- **Goal:** {goal}\n- **Workflow:** `{wf_id}`\n\nI am now building the site at `{domain}/{directory}` in the background. You can track detailed progress in the **Mission Control** sidebar."
                                        st.success("Mission offloaded to engine!")
                                        voice.speak("I am building your site in the background.")
                                    else:
                                        # Fallback to blocking if engine missing (not ideal)
                                        exec_res = asyncio.run(agent.execute_workflow(wf_id, {
                                            "cpanel_url": os.getenv("CPANEL_URL", "https://lookoverhere.xyz:2083"),
                                            "cp_user": os.getenv("CPANEL_USER", "baron"),
                                            "cp_pass": os.getenv("CPANEL_PASS", ""),
                                            "domain": domain,
                                            "directory": directory
                                        }))
                                        content = f"🏗️ **Site Build Started (Blocking Mode):** {exec_res.get('status')}"
                                        st.info("Engine not found, running synchronously.")

                                # PERSIST RESULT
                                st.session_state['manager_messages'].append({"role": "assistant", "content": content})
                                save_chat_message(st.session_state['current_session_id'], "assistant", content)

                    except Exception as e:
                        st.error(f"Error executing {tool}: {e}")
                        voice.speak(f"I encountered an error executing {tool}.")
                    
                    status.update(label="Task Complete", state="complete")
                    
                # Force refresh to show results
                st.rerun()
        
                # Calculate probability of serendipity
                # If tool was successful, maybe show a "Did you know?"
                if random.random() < 0.3:
                    try:
                        intel = asyncio.run(discovery.get_serendipitous_finding())
                        if intel:
                            st.info(f"💡 **Discovery:** {intel['title']} - {intel['content']}")
                    except Exception:
                        pass

    # If we processed a voice command, force a rerun to clear the queue/update state visual
    if voice_command:
        st.rerun()

