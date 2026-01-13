import streamlit as st
import json
from database import (
    get_strategy_presets, save_strategy_preset, delete_strategy_preset
)
from agents import ProductManagerAgent
from ui.agent_lab_ui import render_agent_chat

def render_pm_ui():
    st.header("🏢 Product Lab")
    st.caption("Conceptualize complex products, architect tech specs, and generate outreach strategies.")
    
    st.subheader("Product Manager Mode")
    pm_input = st.text_area("Product/Feature Idea", height=100, placeholder="e.g. 'An automated follow-up system for realtors' or 'A niche SEO report generator'")
    col_pm1, col_pm2 = st.columns(2)
    
    with col_pm1:
        if st.button("Generate Tech Spec", type="primary"):
            if pm_input:
                with st.spinner("PM Agent is architecting..."):
                    agent = ProductManagerAgent()
                    spec = agent.think(pm_input)
                    st.session_state['last_pm_spec'] = spec
                    st.session_state['pm_context'] = pm_input
    
    with col_pm2:
        # === STRATEGY PRESETS UI ===
        presets = get_strategy_presets()
        preset_options = ["Default"] + [p['name'] for p in presets]
        selected_preset_name = st.selectbox("Strategy Preset", preset_options)
        
        # Niche input (now dynamic)
        strat_niche = st.text_input("Target Niche", value="General", help="Used to contextualize the strategy")

        # Manage Presets
        with st.expander("⚙️ Manage Presets"):
            # Create New
            with st.form("new_preset_form"):
                st.write("Create New Strategy Preset")
                np_name = st.text_input("Preset Name")
                np_desc = st.text_input("Description")
                np_instr = st.text_area("Instruction Template", height=150, 
                    placeholder="Develop a strategy for {niche} focusing on aggressive growth... Product: {product_context}",
                    help="Use {niche} and {product_context} as placeholders.")
                if st.form_submit_button("Save Preset"):
                    if np_name and np_instr:
                        save_strategy_preset(np_name, np_desc, np_instr)
                        st.success("Preset saved!")
                        st.rerun()
                    else:
                        st.error("Name and Instructions are required.")
            
            # Delete Existing
            if presets:
                st.divider()
                st.write("Delete Presets")
                p_to_del = st.selectbox("Select to Delete", [p['name'] for p in presets], key="del_preset_sel")
                if st.button("Delete Selected Preset"):
                     pid = next(p['id'] for p in presets if p['name'] == p_to_del)
                     delete_strategy_preset(pid)
                     st.success("Deleted.")
                     st.rerun()

        if st.button("Generate Outreach Strategy"):
            if pm_input:
                with st.spinner("Analyzing market fit and sequence patterns..."):
                    agent = ProductManagerAgent()
                    
                    # Determine instructions
                    custom_instr = None
                    if selected_preset_name != "Default":
                        preset = next(p for p in presets if p['name'] == selected_preset_name)
                        custom_instr = preset['instruction_template']
                    
                    strat = agent.generate_campaign_strategy(pm_input, niche=strat_niche, instruction_template=custom_instr)
                    st.session_state['last_pm_strat'] = strat
                    st.session_state['pm_context'] = pm_input

    if 'last_pm_spec' in st.session_state:
        st.divider()
        st.markdown("### 📄 Technical Specification")
        st.json(st.session_state['last_pm_spec'])
        
        # Export Button
        spec_text = json.dumps(st.session_state['last_pm_spec'], indent=2)
        st.download_button("📥 Export Spec as JSON", spec_text, file_name="tech_spec.json", mime="application/json")
        
        render_agent_chat('last_pm_spec', ProductManagerAgent(), 'pm_context')

    if 'last_pm_strat' in st.session_state:
        st.divider()
        st.markdown("### 🎯 Campaign Strategy")
        st.json(st.session_state['last_pm_strat'])
        
        # Export Button
        strat_text = json.dumps(st.session_state['last_pm_strat'], indent=2)
        st.download_button("📥 Export Strategy as JSON", strat_text, file_name="campaign_strategy.json", mime="application/json")
        
        render_agent_chat('last_pm_strat', ProductManagerAgent(), 'pm_context')
        
        st.markdown("### 🚀 Execution")
        if st.button("🤖 Send to Automation Hub"):
             st.session_state['pending_strategy'] = st.session_state['last_pm_strat']
             st.session_state['current_view'] = "Automation Hub"
             st.rerun()
