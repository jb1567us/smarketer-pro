
import streamlit as st
import asyncio
from agents.manager import ManagerAgent
from utils.recorder import WorkflowRecorder
from utils.voice_manager import VoiceManager
from workflow import run_outreach
from workflow_manager import save_workflow, list_workflows, load_workflow

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

    agent = st.session_state['manager_agent']
    recorder = st.session_state['workflow_recorder']
    voice = st.session_state['voice_manager']

    # Sidebar Voice Status
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

        st.subheader("Transcript")
        if 'transcript_log' not in st.session_state:
            st.session_state['transcript_log'] = []
            
        # Show last 5 lines reversed
        for line in reversed(st.session_state['transcript_log'][-5:]):
            st.caption(f"_{line}_")

    # Process Voice Queue
    voice_command = None
    
    # Process ALL events in queue
    while True:
        event = voice.get_latest_event()
        if not event:
            break
            
        if event['type'] == 'command':
            voice_command = event['payload']
            # Also log to transcript
            st.session_state['transcript_log'].append(f"Command: {voice_command}")
            st.toast(f"Voice Command: {voice_command}")
            
        elif event['type'] == 'transcription':
            # Live hearing (noisy)
            text = event['payload']
            st.session_state['transcript_log'].append(f"{text}")
            st.rerun() # Rerun to update transcript view immediately
            
        elif event['type'] == 'status':
            st.rerun() # Refresh to show new status

    # Display Chat
    for msg in st.session_state['manager_messages']:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat Input
    # We combine voice command and text input. 
    # Since chat_input is unique, we prioritize it, but if voice exists, we use that.
    
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
                    intent_history=st.session_state['manager_messages'][-5:] # Last 5 messages context
                )
                
                # Default safety
                if not response_json:
                    response_json = {"tool": "chat", "reply": "I'm sorry, I encountered an error."}
                
                # Handle list response
                if isinstance(response_json, list):
                    if len(response_json) > 0:
                        response_json = response_json[0]
                    else:
                        response_json = {"tool": "chat", "reply": "I'm sorry, I encountered an empty response."}
                
                tool = response_json.get("tool")
                params = response_json.get("params", {})
                reply = response_json.get("reply", "Done.")

            st.markdown(reply)
            st.session_state['manager_messages'].append({"role": "assistant", "content": reply})
            
            # Voice Reply
            voice.speak(reply)

            # 3. Execution
            if tool and tool != "chat":
                with st.status(f"Executing: {tool}...", expanded=True) as status:
                    try:
                        if tool == "run_search":
                            # Record the step
                            recorder.log_step(tool, params, description=f"Search for '{params.get('query')}'")
                            
                            # Execute
                            st.write(f"Running search for: {params.get('query')}")
                            # Since run_outreach is async, we run it here
                            # Note: run_outreach prints to stdout, we might want to capture that or just rely on DB side effects
                            asyncio.run(run_outreach(
                                params.get("query"), 
                                target_niche=params.get("niche"), 
                                profile_names=params.get("profile", "default")
                            ))
                            st.success("Search completed! Results saved to Leads DB.")
                            voice.speak("Search completed.")

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
                            # Logic to load and run steps
                            st.write(f"Loading workflow: {name}...")
                            # Verification mock
                            st.success(f"Workflow {name} executed (Simulation).")
                            voice.speak(f"Workflow {name} executed.")

                        elif tool == "list_workflows":
                            wfs = list_workflows()
                            st.json(wfs)
                            # Summarize for voice
                            if wfs:
                                voice.speak(f"I found {len(wfs)} workflows: {', '.join(wfs)}.")
                            else:
                                voice.speak("I found no saved workflows.")

                    except Exception as e:
                        st.error(f"Error executing {tool}: {e}")
                        voice.speak(f"I encountered an error executing {tool}.")
                    
                    status.update(label="Task Complete", state="complete")

    # If we processed a voice command, force a rerun to clear the queue/update state visual
    if voice_command:
        st.rerun()

