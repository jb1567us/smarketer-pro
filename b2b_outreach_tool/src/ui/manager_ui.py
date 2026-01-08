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
from utils.agent_registry import get_agent_class, list_available_agents
from memory import Memory
from discovery_engine import DiscoveryEngine

def render_manager_ui():
    st.header("🤖 Manager Agent")
    st.caption("Your personal AI Manager. Ask it to run searches, qualify leads, or automate workflows.")

    # Initialize Session State
    if 'manager_agent' not in st.session_state:
        st.session_state['manager_agent'] = ManagerAgent()
    
    if 'workflow_recorder' not in st.session_state:
        st.session_state['workflow_recorder'] = WorkflowRecorder()
        
    if 'manager_messages' not in st.session_state:
        st.session_state['manager_messages'] = [{"role": "assistant", "content": "How can I help you today?"}]

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
        st.subheader("🎙️ Voice Control")
        
        # Master Switch
        voice_enabled = st.toggle("Enable Voice Listener", value=True)
        
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

    # Display Chat
    for msg in st.session_state['manager_messages']:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

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
                reply = response_json.get("reply", "Done.")

            st.markdown(reply)
            st.session_state['manager_messages'].append({"role": "assistant", "content": reply})
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
                                if isinstance(result, dict) and result.get("image_url"):
                                    # Handle Image Result
                                    img_path = result.get("image_url")
                                    # Streamlit local file text format for markdown images
                                    content_to_display = f"**Task Complete.**\n\n![Generated Image]({img_path})\n\n_Path: {img_path}_"
                                else:
                                    # Handle Text/JSON Result
                                    content_to_display = f"**Result from {agent_name}:**\n```json\n{json.dumps(result, indent=2)}\n```"
                                
                                # Log result to conversation so Manager knows
                                st.session_state['manager_messages'].append({
                                    "role": "assistant", 
                                    "content": content_to_display
                                })
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

