import streamlit as st
import os
import time
import pandas as pd
import json
from agents.designer import GraphicsDesignerAgent
from database import save_creative_content, get_creative_library, delete_creative_item, get_connection
from ui.components import (
    premium_header, safe_action_wrapper, render_enhanced_table, confirm_action, render_page_chat
)
from agents import ManagerAgent

def render_designer_page():
    premium_header("🎨 Creative Designer", "AI-driven visual asset generation for marketing and WordPress design.")

    # Initialize Agent
    if 'designer_agent' not in st.session_state:
        st.session_state['designer_agent'] = GraphicsDesignerAgent()
    
    designer = st.session_state['designer_agent']

    tab_gen, tab_library = st.tabs(["🚀 Generate Assets", "📚 Creative Library"])

    with tab_gen:
        st.subheader("Visual Concept")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            concept = st.text_area(
                "Describe the image you need", 
                value=st.session_state.get('designer_concept_value', ""),
                placeholder="e.g. Editorial illustration for a blog post about modern roofing. Professional, clean, and trustworthy.",
                height=150
            )
        
        with col2:
            style_presets = [
                "Modern Corporate Memphis",
                "Iso-Tech Gradient",
                "Photorealistic Professional",
                "Minimalist Vector",
                "Architectural Sketch",
                "Cinematic 3D Render"
            ]
            style = st.selectbox("Style Preset", style_presets)
            aspect_ratio = st.selectbox("Aspect Ratio", ["16:9 (Blog Header)", "1:1 (Social Post)", "9:16 (Story/Shorts)"])

        if st.button("✨ Generate AI Visual", type="primary", width="stretch"):
            if not concept:
                st.error("Please describe your concept first.")
            else:
                def run_design():
                    return designer.think(concept, instructions=f"Style: {style}. Aspect: {aspect_ratio}")
                
                res = safe_action_wrapper(run_design, "Creative Designer has completed the draft!")
                if res:
                    st.session_state['last_design'] = res
                    # Auto-save to library for history tracking
                    save_creative_content(
                        type="image",
                        title=concept[:50],
                        content_url=res['image_url'],
                        local_path=res.get('local_path'),
                        metadata=json.dumps({"prompt": res.get('revised_prompt'), "style": style, "base_concept": concept})
                    )
                    st.rerun()

        # --- PREVIEW & TWEAK AREA ---
        if 'last_design' in st.session_state:
            res = st.session_state['last_design']
            st.divider()
            st.markdown("#### 👁️ Design Preview")
            
            c_prev, c_tweak = st.columns([1, 1])
            with c_prev:
                if res.get('local_path'):
                    st.image(res['local_path'], caption="Latest Generation")
                else:
                    st.image(res['image_url'], caption="Latest Generation")
            
            with c_tweak:
                st.markdown("**Iterative Feedback**")
                tweak_suggestion = st.text_input("What would you like to change?", placeholder="e.g. Make the colors more vibrant, add a person...")
                if st.button("🔄 Tweak & Regenerate", width="stretch"):
                    if tweak_suggestion:
                        st.session_state['last_design_concept'] = f"Previous layout: {res.get('revised_prompt')}. Adjustment: {tweak_suggestion}"
                        st.info("Concept updated. Click 'Generate AI Visual' again to apply tweaks.")
                        st.session_state['designer_concept_value'] = st.session_state['last_design_concept']
                        st.rerun()

    with tab_library:
        st.subheader("🕵️ Creative Archives")
        library = get_creative_library(type_filter="image")
        
        if not library:
            st.info("No saved assets yet. Start generating in the first tab!")
        else:
            lib_df = pd.DataFrame(library)
            
            # --- Visual Grid for Gallery ---
            st.write(f"Found {len(library)} assets")
            cols = st.columns(3)
            for i, item in enumerate(library):
                with cols[i % 3]:
                    with st.container(border=True):
                        # Display Image
                        if item.get('local_path') and os.path.exists(item['local_path']):
                            st.image(item['local_path'], width="stretch")
                        elif item.get('content_url'):
                             st.image(item['content_url'], width="stretch")
                        else:
                            st.image("https://via.placeholder.com/150", caption="Missing Image")

                        st.caption(f"**{item['title'][:30]}...**")
                        
                        # Actions
                        ac1, ac2 = st.columns(2)
                        with ac1:
                            if st.button("Reuse", key=f"r_{item['id']}"):
                                meta = json.loads(item['metadata']) if isinstance(item['metadata'], str) else item.get('metadata', {})
                                st.session_state['designer_concept_value'] = meta.get('base_concept', item['title'])
                                st.toast("Concept loaded into Generator!")
                        with ac2:
                            confirm_action("🗑️", "Delete?", lambda: [delete_creative_item(item['id']), st.rerun()], key=f"d_gal_{item['id']}")
            
            st.divider()
            with st.expander("Manage Table View"):
                # Enhanced table for bulk
                edited_lib = render_enhanced_table(lib_df[['id', 'title', 'created_at']], key="designer_lib_table")
                
                selected_ids = edited_lib[edited_lib['Select'] == True]['id'].tolist() if 'Select' in edited_lib.columns else []
                if selected_ids:
                    confirm_action("🗑️ Bulk Delete", f"Remove {len(selected_ids)} assets?", 
                                   lambda: [delete_creative_item(lid) for lid in selected_ids], key="bulk_del_design")

    st.divider()
    # Page Level Chat
    render_page_chat("Designer Assistant", ManagerAgent(), "Discuss design concepts and visual strategy.")

    st.markdown("### 📝 Designer as WordPress Lead")
    st.info("The Designer Agent is integrated with the WordPress Manager to provide cohesive visual themes and layouts for new site builds.")
