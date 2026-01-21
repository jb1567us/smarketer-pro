import streamlit as st
import os
from agents.designer import GraphicsDesignerAgent
from database import save_creative_content, get_creative_library, delete_creative_item, get_connection
from ui.components import (
    premium_header, safe_action_wrapper, render_enhanced_table, confirm_action
)
import time
import pandas as pd

def render_designer_page():
    premium_header("🎨 Creative Designer", "AI-driven visual asset generation for marketing and WordPress design.")

    # Initialize Agent
    designer = GraphicsDesignerAgent()

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

        if st.button("✨ Generate AI Visual", type="primary", use_container_width=True):
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
                        metadata={"prompt": res.get('revised_prompt'), "style": style, "base_concept": concept}
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
                if st.button("🔄 Tweak & Regenerate", use_container_width=True):
                    if tweak_suggestion:
                        st.session_state['last_design_concept'] = f"Previous layout: {res.get('revised_prompt')}. Adjustment: {tweak_suggestion}"
                        # Trigger loop logic might need state management, for now we just notify
                        st.info("Concept updated. Click 'Generate AI Visual' again to apply tweaks.")
                        # We can actually automate this by updating the 'concept' variable via session state
                        st.session_state['designer_concept_value'] = st.session_state['last_design_concept']
                        st.rerun()

    with tab_library:
        st.subheader("🕵️ Creative Archives")
        library = get_creative_library(type_filter="image")
        
        if not library:
            st.info("No saved assets yet. Start generating in the first tab!")
        else:
            lib_df = pd.DataFrame(library)
            # Enhanced table for bulk
            edited_lib = render_enhanced_table(lib_df[['id', 'title', 'created_at']], key="designer_lib_table")
            
            selected_ids = edited_lib[edited_lib['Select'] == True]['id'].tolist()
            if selected_ids:
                confirm_action("🗑️ Bulk Delete", f"Remove {len(selected_ids)} assets?", 
                               lambda: [delete_creative_item(lid) for lid in selected_ids], key="bulk_del_design")

            st.divider()
            # Detail/Reuse view
            selected_asset = st.selectbox("Select Asset to View/Iterate", lib_df['title'].tolist())
            if selected_asset:
                item = lib_df[lib_df['title'] == selected_asset].iloc[0]
                with st.container(border=True):
                    img_path = item.get('local_path')
                    if img_path and os.path.exists(img_path):
                        st.image(img_path)
                    else:
                        st.image(item['content_url'])
                    
                    st.markdown(f"**Prompt:** {item.get('metadata', {}).get('prompt', 'N/A')}")
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("🚀 Use as Base for New Design", key=f"reuse_{item['id']}"):
                            st.session_state['designer_concept_value'] = item.get('metadata', {}).get('base_concept', item['title'])
                            st.rerun()
                    with c2:
                         confirm_action("🗑️ Delete Single", "Delete this asset?", lambda: delete_creative_item(item['id']), key=f"del_{item['id']}")

    st.divider()
    st.markdown("### 📝 Designer as WordPress Lead")
    st.info("The Designer Agent is integrated with the WordPress Manager to provide cohesive visual themes and layouts for new site builds.")
    
    with st.expander("Designer Capabilities"):
        st.markdown("""
        - **Blog Headers**: High-quality editorial illustrations.
        - **WordPress Themes**: Brand-aligned color palettes and visual styles.
        - **Social Assets**: Optimized layouts for LinkedIn, Twitter, and Instagram.
        - **Ad Creatives**: High-conversion visual concepts for campaign assets.
        """)
