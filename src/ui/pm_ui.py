import streamlit as st
import json
import time
from database import (
    get_strategy_presets, save_strategy_preset, delete_strategy_preset, update_strategy_preset
)
from agents import ProductManagerAgent
from ui.agent_lab_ui import render_agent_chat
from ui.components import premium_header, confirm_action, safe_action_wrapper, render_page_chat

def render_pm_ui():
    premium_header("🏢 Product Lab", "Conceptualize products and architect outreach strategies.")
    
    st.subheader("Product Manager Mode")
    pm_input = st.text_area("Product/Feature Idea", height=100, placeholder="e.g. 'An automated follow-up system for realtors' or 'A niche SEO report generator'")
    col_pm1, col_pm2 = st.columns(2)
    
    with col_pm1:
        if st.button("Generate Tech Spec", type="primary"):
            if pm_input:
                def run_spec():
                    agent = ProductManagerAgent()
                    return agent.think(pm_input)
                
                with st.spinner("PM Agent is architecting..."):
                    spec = safe_action_wrapper(run_spec, "Tech Spec Generated")
                    if spec:
                        st.session_state['last_pm_spec'] = spec
                        st.session_state['pm_context'] = pm_input
            else:
                st.error("Please provide a product idea.")
    
    with col_pm2:
        # === STRATEGY PRESETS UI ===
        st.subheader("Strategy Presets")
        presets = get_strategy_presets()
        preset_names = ["Default"] + [p['name'] for p in presets]
        
        # State handling for Edit
        if 'pm_edit_mode' not in st.session_state: st.session_state['pm_edit_mode'] = None
        
        selected_preset_name = st.selectbox("Select Strategy Preset", preset_names, key="main_preset_sel")
        
        # Actions Row
        p_col1, p_col2, p_col3 = st.columns(3)
        with p_col1:
             if st.button("➕ New", width="stretch"): 
                 st.session_state['pm_edit_mode'] = "new"
        with p_col2:
             if selected_preset_name != "Default":
                 if st.button("✏️ Edit", width="stretch"):
                     st.session_state['pm_edit_mode'] = "edit"
        with p_col3:
             if selected_preset_name != "Default":
                   def _del():
                       pid = next(p['id'] for p in presets if p['name'] == selected_preset_name)
                       delete_strategy_preset(pid)
                       st.rerun()
                   confirm_action("🗑️", "Delete this preset?", _del, key="del_preset_btn")

        # Edit/Create Form
        if st.session_state['pm_edit_mode']:
             with st.container(border=True):
                 st.write(f"**{st.session_state['pm_edit_mode'].title()} Preset**")
                 
                 # Pre-fill
                 def_name, def_desc, def_instr = "", "", ""
                 if st.session_state['pm_edit_mode'] == 'edit' and selected_preset_name != "Default":
                     curr = next(p for p in presets if p['name'] == selected_preset_name)
                     def_name = curr['name']
                     def_desc = curr['description']
                     def_instr = curr['instruction_template']

                 np_name = st.text_input("Name", value=def_name)
                 np_desc = st.text_input("Description", value=def_desc)
                 np_instr = st.text_area("Template", value=def_instr, height=150, help="Use {niche} and {product_context} placeholders")
                 
                 c1, c2 = st.columns(2)
                 with c1:
                     if st.button("💾 Save", type="primary"):
                         if np_name and np_instr:
                             def save_preset():
                                 if st.session_state['pm_edit_mode'] == 'edit':
                                     pid = next(p['id'] for p in presets if p['name'] == selected_preset_name)
                                     update_strategy_preset(pid, np_name, np_desc, np_instr)
                                 else:
                                     save_strategy_preset(np_name, np_desc, np_instr)
                             
                             safe_action_wrapper(save_preset, "Preset Saved")
                             st.session_state['pm_edit_mode'] = None
                             time.sleep(0.5)
                             st.rerun()
                         else: st.error("Name & Template required.")
                 with c2:
                     if st.button("Cancel"):
                         st.session_state['pm_edit_mode'] = None
                         st.rerun()

        # Niche input (now dynamic)
        strat_niche = st.text_input("Target Niche", value="General", help="Used to contextualize the strategy")

        if st.button("Generate Outreach Strategy", width="stretch"):
            if pm_input:
                def run_strat():
                    agent = ProductManagerAgent()
                    # Determine instructions
                    custom_instr = None
                    if selected_preset_name != "Default":
                        preset = next(p for p in presets if p['name'] == selected_preset_name)
                        custom_instr = preset['instruction_template']
                    
                    return agent.generate_campaign_strategy(pm_input, niche=strat_niche, instruction_template=custom_instr)

                with st.spinner("Analyzing market fit and sequence patterns..."):
                    strat = safe_action_wrapper(run_strat, "Strategy Generated")
                    if strat:
                        st.session_state['last_pm_strat'] = strat
                        st.session_state['pm_context'] = pm_input
            else:
                 st.error("Input required.")

    if 'last_pm_spec' in st.session_state:
        st.divider()
        st.markdown("### 📄 Technical Specification")
        st.json(st.session_state['last_pm_spec'])
        
        # Export Button
        spec_text = json.dumps(st.session_state['last_pm_spec'], indent=2)
        st.download_button("📥 Export Spec as JSON", spec_text, file_name="tech_spec.json", mime="application/json")
        
    if 'last_pm_strat' in st.session_state:
        st.divider()
        st.markdown("### 🎯 Campaign Strategy")
        st.json(st.session_state['last_pm_strat'])
        
        # Export Button
        strat_text = json.dumps(st.session_state['last_pm_strat'], indent=2)
        st.download_button("📥 Export Strategy as JSON", strat_text, file_name="campaign_strategy.json", mime="application/json")
        
        st.markdown("### 🚀 Execution")
        
        def launch_hub():
             st.session_state['pending_strategy'] = st.session_state['last_pm_strat']
             st.session_state['current_view'] = "Automation Hub" # Assuming this view exists or similar logic
             st.toast("Redirecting to Automation Hub...")
             time.sleep(1)
             st.rerun()

        confirm_action("🚀 Launch Campaign", "Send this strategy to the Automation Hub for execution?", launch_hub, key="launch_strat_btn")

    # Unified Chat
    render_page_chat("Product Architect", ProductManagerAgent(), "Iterate on product specs and go-to-market strategies.")
