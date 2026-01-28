import streamlit as st
import asyncio
from agents import ManagerAgent

def render_strategy_lab():
    """Renders the Strategy Laboratory UI component."""
    st.header("🔬 Strategy Laboratory")
    st.caption("Conceptualize complex campaigns and manage collective agent intelligence.")
    
    lab_tabs = st.tabs(["🔗 Multichannel sequence", "🧠 Memory Browser"])
    
    with lab_tabs[0]:
        st.subheader("Multichannel Sequence Planner")
        st.write("The Manager Agent will plan a multi-touch sequence across Email and LinkedIn.")
        m_goal = st.text_input("Campaign Goal", placeholder="e.g. 'Find 5 SEO agencies and draft multi-touch outreach'")
        
        if st.button("Plan & Draft Mission"):
            if m_goal:
                with st.status("Manager orchestrating mission...", expanded=True) as status:
                    agent = ManagerAgent()
                    report = asyncio.run(agent.run_mission(m_goal))
                    st.session_state['last_mission_report'] = report
                    st.session_state['mission_context'] = m_goal
                    status.update(label="Mission Planned!", state="complete")
        
        if 'last_mission_report' in st.session_state:
            report = st.session_state['last_mission_report']
            st.divider()
            st.markdown(f"### 📋 Mission Report: {report['plan'].get('strategy_name', 'Custom Mission')}")
            st.write(f"**ICP:** {report['plan'].get('icp_criteria')}")
            
            for idx, lead in enumerate(report.get('leads', [])):
                with st.expander(f"👤 Lead: {lead.get('url', 'Unknown URL')}"):
                    st.write("**Drafts:**")
                    drafts = lead.get('drafts', {})
                    if 'email' in drafts:
                        st.markdown("--- Email ---")
                        st.json(drafts['email'])
                    if 'linkedin' in drafts:
                        st.markdown("--- LinkedIn ---")
                        st.json(drafts['linkedin'])

    with lab_tabs[1]:
        st.subheader("🧠 Memory Browser")
        st.write("Browse recorded agent thoughts and decision paths.")
        
        # Fetch memory
        try:
            from memory import memory_store
            memory_data = memory_store.get_all_memory() # Returns dict {agent_role: {key: {content, timestamp, metadata}}}
        except ImportError:
            st.error("Memory store not available.")
            memory_data = None
        
        if not memory_data:
            st.info("Neural network is fresh. No memories recorded yet.")
        else:
            roles = ["All Agents"] + sorted(list(memory_data.keys()))
            sel_role = st.selectbox("🤖 Filter Agent memories", roles)
            
            search_q = st.text_input("🔍 Search memories", placeholder="Keyword...")
            
            if search_q:
                # Logic for search (simplified/placeholder if not fully implemented in memory_store)
                st.info(f"Searching for '{search_q}' in {sel_role} memories...")
            else:
                # Grouped Index
                if sel_role == "All Agents":
                    for role, entries in memory_data.items():
                        with st.expander(f"🤖 {role} ({len(entries)} entries)"):
                            for key, data in entries.items():
                                st.markdown(f"**{key}:** {data['content']}")
                                st.divider()
                else:
                    entries = memory_data.get(sel_role, {})
                    st.write(f"Showing memories for: **{sel_role}**")
                    for key, data in entries.items():
                        with st.expander(f"🔑 {key}"):
                            st.write(data['content'])
                            st.caption(f"Recorded: {data['timestamp']}")
