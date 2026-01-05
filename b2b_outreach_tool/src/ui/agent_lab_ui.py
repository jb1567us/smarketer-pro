import streamlit as st
import json
from agents import (
    ResearcherAgent, QualifierAgent, CopywriterAgent, ManagerAgent,
    GraphicsDesignerAgent, SocialMediaAgent, AdCopyAgent, BrainstormerAgent,
    PersonaAgent, WordPressAgent, ProductManagerAgent, LinkedInAgent,
    ReviewerAgent, SyntaxAgent, UXAgent, SEOExpertAgent, VideoAgent
)

# Registry of Standard Agents
AGENTS = {
    "Researcher": ResearcherAgent,
    "Qualifier": QualifierAgent,
    "Copywriter": CopywriterAgent,
    "Manager": ManagerAgent,
    "Graphics Designer": GraphicsDesignerAgent,
    "Social Media Strategist": SocialMediaAgent,
    "Ad Copywriter": AdCopyAgent,
    "Brainstormer": BrainstormerAgent,
    "Persona Analyst": PersonaAgent,
    "WordPress Expert": WordPressAgent,
    "Product Manager": ProductManagerAgent,
    "LinkedIn Specialist": LinkedInAgent,
    "Content Reviewer": ReviewerAgent,
    "Syntax Validator": SyntaxAgent,
    "UX Designer": UXAgent,
    "SEO Expert": SEOExpertAgent,
    "Video Director": VideoAgent
}

def render_agent_lab():
    """
    Renders the Agent Lab UI for interacting with standard agents.
    Includes 'System Prompt / Instructions' tweak.
    """
    st.header("🧪 Agent Lab")
    st.caption("Directly interact with system agents for testing and one-off tasks.")

    col1, col2 = st.columns([3, 1])
    with col1:
        agent_name = st.selectbox("Select Agent", sorted(list(AGENTS.keys())))
    
    agent_class = AGENTS[agent_name]
    
    # Instantiate the agent
    # Most agents use default provider/model from .env or internal config
    try:
        agent = agent_class()
    except Exception:
        # Fallback if init requires args (shouldn't for these standard ones)
        agent = agent_class(provider=None) 
    
    with st.container(border=True):
        st.markdown(f"**Role:** {agent.role}")
        st.markdown(f"**Goal:** {agent.goal}")
    
    # Input Area
    context = st.text_area(
        "Context / Input Data", 
        height=200, 
        placeholder="Paste data, text, or instructions here...",
        help="The main content the agent will process."
    )
    
    # SYSTEM PROMPT TWEAK
    with st.expander("🛠️ Advanced: System Instructions"):
        st.info("💡 Inject additional rules, persona tweaks, or constraints into the agent's system prompt for this run.")
        user_instructions = st.text_area(
            "Additional Instructions", 
            height=100, 
            placeholder="e.g., 'Be extremely sarcastic.', 'Output as CSV only.', 'Focus on verifyable facts.'"
        )
    
    if st.button("Run Agent", type="primary"):
        if context:
            with st.spinner(f"{agent.role} is thinking..."):
                try:
                    # Pass the instructions (Tweak)
                    # All agents should now support this optional arg
                    response = agent.think(context, instructions=user_instructions if user_instructions else None)
                    
                    st.session_state['last_lab_response'] = response
                    st.session_state['last_lab_agent_instance'] = agent 
                    st.session_state['last_lab_context'] = context
                    st.rerun()
                except Exception as e:
                    st.error(f"Error during execution: {str(e)}")
        else:
            st.warning("Please provide context to run the agent.")

    # Result & Tuning Section
    if 'last_lab_response' in st.session_state:
        st.divider()
        st.subheader("Result")
        
        response = st.session_state['last_lab_response']
        
        # Determine if it's JSON or Text to display nicely
        if isinstance(response, (dict, list)):
             st.json(response)
        else:
             st.write(response)
             
        # Tuning / Discussion
        # Only show if the current agent matches the one that ran
        # We stored the instance, but strict equality might fail on rerun if re-instantiated.
        # So we check name implicitly or just use the stored instance for logic.
        
        # We use a shared function for Tuning to handle both Lab and Custom Agents
        # We need to pass the ST_SESSION_STATE keys where data is stored
        render_agent_chat('last_lab_response', st.session_state['last_lab_agent_instance'], 'last_lab_context')


def render_agent_chat(response_key, agent_instance, context_key):
    """
    Renders a chat interface for tuning/discussing with an agent after a result.
    response_key: session_state key where the last response is stored.
    agent_instance: the agent object.
    context_key: session_state key where the original context is stored.
    """
    st.divider()
    st.subheader("💬 Discussion & Tuning")
    st.caption("Not satisfied? Ask the agent to refine, rewrite, or explain.")

    # Initialize chat history for this session if needed
    # We key it by the response key to reset on new runs
    history_key = f"chat_history_{response_key}"
    if history_key not in st.session_state:
        st.session_state[history_key] = []

    # Display History
    for msg in st.session_state[history_key]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Chat Input
    if user_input := st.chat_input("Refine this output (e.g., 'Make it shorter', 'Change tone to professional')..."):
        # Add user message
        st.session_state[history_key].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        # Agent Action
        with st.chat_message("assistant"):
            with st.spinner("Refining..."):
                # We need context and previous response
                original_context = st.session_state.get(context_key, "")
                previous_response = st.session_state.get(response_key)
                
                # We call agent.tune() which handles the refinement logic
                # logic: tune(context, previous_response, instructions, history)
                # Note: history might be needed if base agent supports it
                # For now we just pass specific instructions
                
                try:
                    # Check if agent has tune method (BaseAgent does)
                    new_response = agent_instance.tune(original_context, previous_response, user_input)
                    
                    # Display
                    if isinstance(new_response, (dict, list)):
                        st.json(new_response)
                        # Convert to string for chat history
                        msg_content = f"```json\n{json.dumps(new_response, indent=2)}\n```"
                    else:
                        st.write(new_response)
                        msg_content = str(new_response)
                    
                    # Update History & Main State?
                    # Usually we update history. We might also update the "Main Result" if it was a strict refinement.
                    # But keeping history is safer.
                    st.session_state[history_key].append({"role": "assistant", "content": msg_content})
                    
                    # Optional: Update the 'last response' so subsequent tunes work on the NEW version?
                    # Yes, that's usually expected in a "tune" loop.
                    st.session_state[response_key] = new_response
                    
                except Exception as e:
                    st.error(f"Tuning failed: {str(e)}")

# Alias for backwards compatibility if app.py imports it
render_tuning_dialog = render_agent_chat
