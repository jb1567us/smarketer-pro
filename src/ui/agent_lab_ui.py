import streamlit as st
import json
import time
import functools
from agents import (
    ResearcherAgent, QualifierAgent, CopywriterAgent, ManagerAgent,
    GraphicsDesignerAgent, WordPressAgent, ProductManagerAgent, LinkedInAgent,
    ReviewerAgent, SyntaxAgent, UXAgent, SEOExpertAgent, VideoAgent,
    ContactFormAgent, InfluencerAgent
)
from ui.components import premium_header, safe_action_wrapper

# Registry of Standard Agents
AGENTS = {
    "Researcher": ResearcherAgent,
    "Qualifier": QualifierAgent,
    "Copywriter": CopywriterAgent,
    "Manager": ManagerAgent,
    "Graphics Designer": GraphicsDesignerAgent,
    "Social Media Strategist": functools.partial(CopywriterAgent, role="Expert Social Media Strategist", goal="Generate high-engagement social media posts for various platforms."),
    "Ad Copywriter": functools.partial(CopywriterAgent, role="Direct Response Copywriter", goal="Write high-converting ad copy for Google, Facebook, and LinkedIn."),
    "Brainstormer": functools.partial(CopywriterAgent, role="Creative Campaign Director", goal="Brainstorm innovative campaign angles, hooks, and themes."),
    "Persona Analyst": functools.partial(CopywriterAgent, role="Market Research Analyst", goal="Create detailed Ideal Customer Personas (ICPs) based on market data."),
    "WordPress Expert": WordPressAgent,
    "Product Manager": ProductManagerAgent,
    "LinkedIn Specialist": LinkedInAgent,
    "Reviewer": ReviewerAgent,
    "Syntax Validator": SyntaxAgent,
    "UX Designer": UXAgent,
    "SEO Expert": SEOExpertAgent,
    "Video Director": VideoAgent,
    "Contact Form Specialist": ContactFormAgent,
    "Influencer Scout": InfluencerAgent
}

# Categorized Mapping
AGENT_CATEGORIES = {
    "Research & Leads": ["Researcher", "Qualifier", "Persona Analyst", "LinkedIn Specialist", "Contact Form Specialist", "Influencer Scout"],
    "Marketing & Content": ["Copywriter", "Graphics Designer", "Social Media Strategist", "Ad Copywriter", "Video Director", "Brainstormer"],
    "SEO & Growth": ["SEO Expert", "WordPress Expert", "UX Designer"],
    "System & Admin": ["Manager", "Product Manager", "Reviewer", "Syntax Validator"]
}

def render_agent_lab():
    """
    Renders the Agent Lab UI for interacting with standard agents.
    Includes 'System Prompt / Instructions' tweak.
    """
    premium_header("🧪 Agent Lab", "Directly interact with specialized agents organized by capability.")

    # 1. Category Tabs
    cat_names = list(AGENT_CATEGORIES.keys())
    tabs = st.tabs(cat_names)
    
    # 2. Render Agent Selector inside each tab
    # We use a session state variable to track the globally active agent
    if 'active_lab_agent' not in st.session_state:
        st.session_state['active_lab_agent'] = "Researcher" # Default

    for i, tab in enumerate(tabs):
        with tab:
            category = cat_names[i]
            agents_in_cat = AGENT_CATEGORIES[category]
            
            # Find index of current active agent if it belongs to this category
            try:
                curr_index = agents_in_cat.index(st.session_state['active_lab_agent'])
            except ValueError:
                curr_index = 0
            
            # Using a unique key per tab but updating the global state
            # We use a selectbox or pills for better visibility
            selection = st.radio(
                f"Select {category} Agent", 
                options=agents_in_cat, 
                horizontal=True,
                label_visibility="collapsed",
                index=curr_index if st.session_state['active_lab_agent'] in agents_in_cat else 0,
                key=f"cat_{i}_selector"
            )
            
            # If the selection here is different/clicked, update global?
            # Streamlit logic: The radio 'key' holds the value.
            # But we want multiple radios to sync. This is hard.
            # INSTEAD: We will just check if this specific radio matches the global state.
            
            # Simple workaround: Just a button to "Activate" if we want to be strict,
            # OR we just accept that the user clicks the radio and we treat it as active.
            # To simplify: We'll just render the interaction area for the LOCALLY selected agent in this tab.
            
            if selection:
                 render_agent_interaction_area(selection)


def render_agent_interaction_area(agent_name):
    """
    Renders the interaction area for the specifically selected agent.
    """
    if not agent_name: 
        return

    agent_class = AGENTS.get(agent_name)
    if not agent_class:
        st.error(f"Agent class not found for {agent_name}")
        return
        
    # Instantiate the agent
    try:
        agent = agent_class()
    except Exception:
        agent = agent_class(provider=None) 
    
    st.divider()
    
    # Header for the specific agent area
    c1, c2 = st.columns([1, 4])
    with c1:
        st.write("") # Spacer or Icon
        st.markdown(f"### 🤖") 
    with c2:
        st.markdown(f"**{agent_name}**")
        st.caption(f"{agent.role} • {agent.goal[:100]}...")

    # Special UI for Influencer Scout
    platform_selection = None
    if agent_name == "Influencer Scout":
        platform_selection = st.selectbox(
            "Select Target Platform",
            ["instagram", "tiktok", "youtube", "twitter", "linkedin"],
            key=f"platform_{agent_name}"
        )
        
        limit_selection = st.slider(
            "Max Results Goal",
            min_value=10,
            max_value=2000,
            value=50,
            step=10,
            help="Target number of influencers to discover.",
            key=f"limit_{agent_name}"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            min_followers = st.text_input("Min Followers (e.g. 10k)", key=f"min_f_{agent_name}")
        with col2:
            max_followers = st.text_input("Max Followers", key=f"max_f_{agent_name}")


    # Input Area
    # We use a unique key for the text area based on the agent name 
    # so input is preserved per agent (which is a nice feature!)
    context = st.text_area(
        "Context / Input Data", 
        height=200, 
        placeholder=f"Enter information for the {agent_name}...",
        help="The main content the agent will process.",
        key=f"input_{agent_name}" 
    )
    
    # SYSTEM PROMPT TWEAK
    with st.expander("🛠️ Advanced: System Instructions"):
        st.info("💡 Inject additional rules, persona tweaks, or constraints.")
        user_instructions = st.text_area(
            "Additional Instructions", 
            height=100, 
            placeholder="e.g., 'Be extremely sarcastic.', 'Output as CSV only.'",
            key=f"instr_{agent_name}"
        )
    
    if st.button(f"Run {agent_name}", type="primary", key=f"run_{agent_name}", disabled=not context):
        if context:
            # Prepend platform if applicable
            final_context = context
            if platform_selection:
                final_context = f"Target Platform: {platform_selection}\n"
                
            if agent_name == "Influencer Scout" and 'limit_selection' in locals():
                 final_context += f"Target Limit: {limit_selection}\n"
                 if 'min_followers' in locals() and min_followers: final_context += f"Min Followers: {min_followers}\n"
                 if 'max_followers' in locals() and max_followers: final_context += f"Max Followers: {max_followers}\n"
            
            final_context += f"\n{context}"

            with st.spinner(f"{agent.role} is thinking..."):
                def run_thought():
                     return agent.think(final_context, instructions=user_instructions if user_instructions else None)
                
                response = safe_action_wrapper(run_thought, "Agent finished thinking!")
                if response:
                    st.session_state['last_lab_response'] = response
                    st.session_state['last_lab_agent_instance'] = agent 
                    st.session_state['last_lab_context'] = context
                    st.session_state['last_lab_agent_name'] = agent_name # Track which agent ran
                    st.rerun()
        else:
            st.warning("Please provide context to run the agent.")

    # Result & Tuning Section
    # We only show this if the LAST run agent matches the CURRENT rendered agent
    # This avoids showing "Researcher" results in the "Copywriter" tab.
    if 'last_lab_response' in st.session_state:
        if st.session_state.get('last_lab_agent_name') == agent_name:
            st.divider()
            st.subheader("Result")
            
            response = st.session_state['last_lab_response']
            
            if isinstance(response, (dict, list)):
                 st.json(response)
            else:
                 st.write(response)
                 
            # Export / Persistence
            st.markdown("#### Export")
            res_str = json.dumps(response, indent=2) if isinstance(response, (dict, list)) else str(response)
            st.download_button(
                 label="📥 Download Result (JSON)",
                 data=res_str,
                 file_name=f"{agent_name}_result_{int(time.time())}.json",
                 mime="application/json"
            )
            
            # Tuning / Discussion
            render_agent_chat('last_lab_response', st.session_state['last_lab_agent_instance'], 'last_lab_context')
        else:
            # Maybe show a small note that results are in another tab? 
            # No, cleaner to just show nothing here.
            pass


def render_agent_chat(response_key, agent_instance, context_key):
    """
    Renders a chat interface for tuning/discussing with an agent after a result.
    response_key: session_state key where the last response is stored.
    agent_instance: the agent object.
    context_key: session_state key where the original context is stored.
    """
    if response_key not in st.session_state:
        return

    st.divider()
    st.subheader("💬 Discussion & Tuning")
    st.caption("Not satisfied? Ask the agent to refine, rewrite, or explain.")

    # Initialize chat history for this session if needed
    history_key = f"chat_history_{response_key}"
    if history_key not in st.session_state:
        st.session_state[history_key] = []

    # Mode Selection
    mode = st.radio(
        "Action:", 
        ["Discuss (Chat)", "Refine (Update Output)"], 
        horizontal=True, 
        key=f"mode_{response_key}",
        help="'Discuss' just asks questions. 'Refine' asks the agent to rewrite the output."
    )

    # Display History
    for msg in st.session_state[history_key]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"]) # Use markdown for better rendering

    # Chat Input
    if user_input := st.chat_input(f"Message the {agent_instance.role}..."):
        # Add user message
        st.session_state[history_key].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Agent Action
        with st.chat_message("assistant"):
            with st.spinner(f"{'Refining' if 'Refine' in mode else 'Thinking'}..."):
                original_context = st.session_state.get(context_key, "")
                previous_response = st.session_state.get(response_key)
                
                # Retrieve history string for context
                # simplified history text for the LLM
                hist_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state[history_key]])
                
                try:
                    new_response = None
                    display_content = ""
                    
                    if "Refine" in mode:
                        # TUNE / ITERATE
                        new_response = agent_instance.tune(original_context, previous_response, user_input, history=hist_text)
                        
                        # Update the Main Result State
                        st.session_state[response_key] = new_response
                        
                        if isinstance(new_response, (dict, list)):
                            display_content = f"**Refined Output:**\n```json\n{json.dumps(new_response, indent=2)}\n```"
                        else:
                            display_content = f"**Refined Output:**\n{new_response}"
                            
                    else:
                        # DISCUSS
                        new_response = agent_instance.discuss(original_context, previous_response, user_input, history=hist_text)
                        display_content = new_response

                    st.markdown(display_content)
                    st.session_state[history_key].append({"role": "assistant", "content": display_content})
                    
                    if "Refine" in mode:
                        st.success("Output updated!")
                        time.sleep(1) # Brief pause to show success
                        st.rerun() # Rerun to update the main view above
                    
                except Exception as e:
                    st.error(f"Agent failed: {str(e)}")

# Alias for backwards compatibility if app.py imports it
render_tuning_dialog = render_agent_chat
