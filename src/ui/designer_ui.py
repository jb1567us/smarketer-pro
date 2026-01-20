import streamlit as st
import os
from agents.designer import GraphicsDesignerAgent
from database import save_creative_content, get_creative_library, delete_creative_item
import time

def render_designer_page():
    st.header("🎨 Creative Designer")
    st.caption("AI-driven visual asset generation for marketing and WordPress design.")

    # Initialize Agent
    designer = GraphicsDesignerAgent()

    tab_gen, tab_library = st.tabs(["🚀 Generate Assets", "📚 Creative Library"])

    with tab_gen:
        st.subheader("Visual Concept")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            concept = st.text_area(
                "Describe the image you need", 
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
                with st.spinner("AI Designer is drafting and rendering your visual..."):
                    try:
                        # Call Agent
                        res = designer.think(concept, instructions=f"Style: {style}. Aspect: {aspect_ratio}")
                        
                        st.success("Visual Asset Generated!")
                        
                        # Display
                        if res.get('local_path'):
                            st.image(res['local_path'], caption=res.get('revised_prompt', 'AI Generated Visual'))
                        else:
                            st.image(res['image_url'], caption=res.get('revised_prompt', 'AI Generated Visual'))
                        
                        # Save to Library
                        if st.button("📥 Save to Creative Library"):
                            save_creative_content(
                                type="image",
                                title=concept[:50],
                                content_url=res['image_url'],
                                local_path=res.get('local_path'),
                                metadata={"prompt": res.get('revised_prompt'), "style": style}
                            )
                            st.toast("Saved to Creative Library!")
                            
                    except Exception as e:
                        st.error(f"Generation failed: {e}")

    with tab_library:
        st.subheader("My Creative Assets")
        library = get_creative_library(type_filter="image")
        
        if not library:
            st.info("No saved assets yet. Start generating in the first tab!")
        else:
            # Display in a grid
            cols = st.columns(3)
            for i, item in enumerate(library):
                with cols[i % 3]:
                    with st.container(border=True):
                        # Use local path if it exists, else URL
                        img_path = item.get('local_path')
                        if img_path and os.path.exists(img_path):
                            st.image(img_path)
                        else:
                            st.image(item['content_url'])
                            
                        st.write(f"**{item['title']}**")
                        st.caption(f"Style: {item.get('metadata', {}).get('style', 'N/A')}")
                        
                        if st.button("🗑️ Delete", key=f"del_{item['id']}"):
                            delete_creative_item(item['id'])
                            st.rerun()

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
