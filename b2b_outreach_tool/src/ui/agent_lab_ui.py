import streamlit as st
import json
from agents import (
    ResearcherAgent, QualifierAgent, CopywriterAgent, ManagerAgent,
    GraphicsDesignerAgent, SocialMediaAgent, AdCopyAgent, BrainstormerAgent,
    PersonaAgent, WordPressAgent, ProductManagerAgent, LinkedInAgent,
    ReviewerAgent, SyntaxAgent, UXAgent, SEOExpertAgent, VideoAgent,
    ContactFormAgent
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
    "Reviewer": ReviewerAgent,
    "Syntax Validator": SyntaxAgent,
    "UX Designer": UXAgent,
    "SEO Expert": SEOExpertAgent,
    "Video Director": VideoAgent,
    "Contact Form Specialist": ContactFormAgent
}

# Categorized Mapping
AGENT_CATEGORIES = {
    "Research & Leads": ["Researcher", "Qualifier", "Persona Analyst", "LinkedIn Specialist", "Contact Form Specialist"],
    "Marketing & Content": ["Copywriter", "Graphics Designer", "Social Media Strategist", "Ad Copywriter", "Video Director", "Brainstormer"],
    "SEO & Growth": ["SEO Expert", "WordPress Expert", "UX Designer"],
    "System & Admin": ["Manager", "Product Manager", "Reviewer", "Syntax Validator"]
}

def render_agent_lab():
    """
    Renders the Agent Lab UI for interacting with standard agents.
    Includes 'System Prompt / Instructions' tweak.
    """
    st.header("🧪 Agent Lab")
    st.caption("Directly interact with specialized agents organized by capability. (v2.0 Fixed)")

    # 1. Category Tabs
    # We use tabs to split the 18+ agents into manageable chunks
    cat_names = list(AGENT_CATEGORIES.keys())
    tabs = st.tabs(cat_names)
    
    selected_agent_name = None
    
    # 2. Render Agent Selector inside each tab
    for i, tab in enumerate(tabs):
        with tab:
            category = cat_names[i]
            agents_in_cat = AGENT_CATEGORIES[category]
            
            # Using radio with horizontal=True acts like a sub-tab/pill selector
            # We explicitly namespace the key to avoid collisions if we switched back and forth
            # But since we need ONE global selection, we might need a unified state approach.
            # However, st.radio in tabs is tricky because switching tabs hides the radio but keeps state.
            
            # Better Approach:
            # We can't easily have 4 radios all binding to "selected_agent".
            # So we let the user click a radio button, and we immediately update a session state var manually if needed,
            # OR we just rely on visual layout.
            
            # Simple Fix: Just render the radio for this tab. 
            # If the user selects something here, it becomes the 'active' agent.
            # To avoid "None" issues, we default to the first one in the First tab if nothing set.
            
            selection = st.radio(
                f"Select {category} Agent", 
                options=agents_in_cat, 
                horizontal=True,
                label_visibility="collapsed",
                key=f"cat_{i}_selector"
            )
            
            # We need to know WHICH tab is active to know which selection to honor.
            # Streamlit doesn't give "active_tab" state easily without 3rd party components.
            # Workaround: We'll put a "Load Agent" button or similar? 
            # No, that's clunky.
            
            # Alternative: One single sidebar selectbox is what we had, but it was too long.
            # Let's try to infer: The user sees the tab they opened.
            # The radio button in THAT tab is what they are interacting with.
            # BUT, all 4 radios exist in the DOM/Backend.
            
            # We will use a container to show the ACTIVE agent below the tabs.
            # We need to track "last_selected_category" maybe?
            
            # Actually, standard Streamlit pattern for this:
            # Use columns or just one big area below.
            # But how to determine which of the 4 radios is "The One"?
            # They all have values. 
            
            # Refined Approach:
            # We use `st.pills` if available (st >= 1.40). If not, radio.
            # Let's assume standard radio. 
            
            # To make it work: We can use a callback or check which one changed?
            # Or simpler: Just put the "Run" UI *inside* the tab?
            # Yes! That guarantees context.
            
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
    
    if st.button(f"Run {agent_name}", type="primary", key=f"run_{agent_name}"):
        if context:
            with st.spinner(f"{agent.role} is thinking..."):
                try:
                    response = agent.think(context, instructions=user_instructions if user_instructions else None)
                    
                    st.session_state['last_lab_response'] = response
                    st.session_state['last_lab_agent_instance'] = agent 
                    st.session_state['last_lab_context'] = context
                    st.session_state['last_lab_agent_name'] = agent_name # Track which agent ran
                    st.rerun()
                except Exception as e:
                    st.error(f"Error during execution: {str(e)}")
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
    if user_input := st.chat_input("Refine this output (e.g., 'Make it shorter', 'Change tone')..."):
        # Add user message
        st.session_state[history_key].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        # Agent Action
        with st.chat_message("assistant"):
            with st.spinner("Refining..."):
                original_context = st.session_state.get(context_key, "")
                previous_response = st.session_state.get(response_key)
                
                try:
                    new_response = agent_instance.tune(original_context, previous_response, user_input)
                    
                    if isinstance(new_response, (dict, list)):
                        st.json(new_response)
                        msg_content = f"```json\n{json.dumps(new_response, indent=2)}\n```"
                    else:
                        st.write(new_response)
                        msg_content = str(new_response)
                    
                    st.session_state[history_key].append({"role": "assistant", "content": msg_content})
                    st.session_state[response_key] = new_response
                    
                except Exception as e:
                    st.error(f"Tuning failed: {str(e)}")

# Alias for backwards compatibility if app.py imports it
render_tuning_dialog = render_agent_chat
