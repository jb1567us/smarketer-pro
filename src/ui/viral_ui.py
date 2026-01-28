import streamlit as st
import json
from agents.creative import SocialMediaAgent
from ui.agent_lab_ui import render_agent_chat
from database import save_creative_content

def render_viral_engine():
    """Renders the Viral Engine UI component."""
    st.header("🚀 Viral Engine")
    st.caption("Generate high-velocity content ideas for TikTok, Reels, and Shorts.")
    
    # Initialize Agent
    if 'viral_agent' not in st.session_state:
        st.session_state['viral_agent'] = SocialMediaAgent()
    agent = st.session_state['viral_agent']
    
    col1, col2 = st.columns(2)
    with col1:
        v_niche = st.text_input("Target Niche", placeholder="e.g. AI Productivity Tools", key="ve_niche")
    with col2:
        v_product = st.text_input("Product/Focus", placeholder="e.g. Smarketer Pro", key="ve_prod")
        
    v_platform = st.selectbox("Platform Strategy", ["TikTok Viral", "Instagram Reels", "YouTube Shorts"], key="ve_plat")
    
    if st.button("Generate Viral Concepts", type="primary"):
         if v_niche and v_product:
             with st.spinner("Analyzing trends and generating hooks..."):
                 context = f"Product: {v_product}, Niche: {v_niche}, Platform: {v_platform}"
                 if v_platform == "TikTok Viral":
                     res = agent.generate_tiktok_strategy(v_niche, v_product)
                 elif v_platform == "Instagram Reels":
                     res = agent.generate_instagram_strategy(v_niche, v_product)
                 else:
                     # Fallback/Custom
                     res = agent.think(f"Generate a viral YouTube Shorts strategy for {v_product} in the {v_niche} niche. Include 3 video concepts with hooks and script outlines.")
                 
                 st.session_state['viral_results'] = res
                 st.session_state['viral_context'] = context
                 st.rerun()
         else:
             st.warning("Please enter Niche and Product.")
             
    if 'viral_results' in st.session_state:
        st.divider()
        st.subheader("🔥 Strategy Output")
        st.json(st.session_state['viral_results'])
        
        # Interactive Chat
        render_agent_chat('viral_results', agent, 'viral_context')

        # Save to Library
        if st.button("💾 Save Strategy"):
             save_creative_content(
                 "Social Media", "json", 
                 f"Viral Strategy: {v_product}", 
                 json.dumps(st.session_state['viral_results'])
             )
             st.toast("Strategy Saved!")
