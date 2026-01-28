import streamlit as st
import time
from database import create_custom_agent, get_custom_agents, delete_custom_agent
from agents.custom_agent import CustomAgent
from ui.agent_lab_ui import render_agent_chat

def render_agent_factory():
    """Renders the Agent Factory UI component."""
    st.header("🏭 Agent Factory")
    st.caption("Create and manage custom AI agents for specific tasks.")
    
    tab_list, tab_create, tab_run = st.tabs(["📂 My Agents", "➕ Create Agent", "🤖 Run Agent"])
    
    with tab_create:
        st.subheader("Define New Agent")
        with st.form("create_agent_form"):
            ca_name = st.text_input("Agent Name", placeholder="e.g. Poet, Code Reviewer")
            ca_role = st.text_input("Role", placeholder="e.g. Senior Poet, Python Expert")
            ca_goal = st.text_area("Goal", placeholder="e.g. Write beautiful haikus about specific topics.")
            ca_sys = st.text_area("System Prompt (Optional)", placeholder="Base instructions/personality...", height=150)
            
            if st.form_submit_button("Create Agent", type="primary"):
                if ca_name and ca_role and ca_goal:
                    create_custom_agent(ca_name, ca_role, ca_goal, ca_sys)
                    st.success(f"Agent '{ca_name}' created successfully!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Name, Role, and Goal are required.")

    with tab_list:
        st.subheader("Installed Agents")
        agents = get_custom_agents()
        if not agents:
            st.info("No custom agents found. Create one in the next tab!")
        else:
            for ag in agents:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([1, 3, 1])
                    with c1:
                        st.subheader(f"🤖 {ag['name']}")
                    with c2:
                        st.write(f"**Role:** {ag['role']}")
                        st.write(f"**Goal:** {ag['goal']}")
                    with c3:
                        if st.button("Delete", key=f"del_ag_{ag['id']}"):
                            delete_custom_agent(ag['id'])
                            st.rerun()

    with tab_run:
        st.subheader("Run Custom Agent")
        agents = get_custom_agents()
        if not agents:
            st.warning("Create an agent first!")
        else:
            selected_agent_name = st.selectbox("Select Agent", [a['name'] for a in agents])
            # Get full agent details
            selected_agent_data = next(a for a in agents if a['name'] == selected_agent_name)
            
            # Instantiate Agent
            custom_agent = CustomAgent(
                name=selected_agent_data['name'],
                role=selected_agent_data['role'],
                goal=selected_agent_data['goal'],
                system_prompt=selected_agent_data['system_prompt']
            )
            
            # Context Input
            context_input = st.text_area("Context / Input", height=150, key="ca_context", placeholder="Enter the text or data the agent should process...")
            
            # Proxy Toggle
            use_proxies = st.checkbox("Use Elite Proxy Pool", value=True, help="Enable if this agent performs web tasks or needs higher anonymity.")
            custom_agent.proxy_enabled = use_proxies

            if st.button("Run Agent", type="primary"):
                if context_input:
                    with st.spinner(f"{selected_agent_name} is thinking..."):
                        response = custom_agent.think(context_input)
                        st.session_state['last_custom_agent_response'] = response
                        st.rerun()
                else:
                    st.error("Please provide some input.")
            
            # Show Result & Tuning
            if 'last_custom_agent_response' in st.session_state:
                st.divider()
                st.subheader("Result")
                st.write(st.session_state['last_custom_agent_response'])
                
                # Agent Lab Tuning Integration
                render_agent_chat("last_custom_agent_response", custom_agent, "ca_context")
