import streamlit as st
import pandas as pd
import json
import time
from database import get_creative_library, delete_creative_item
from ui.components import render_data_management_bar, render_enhanced_table, render_page_chat
from agents import CopywriterAgent

def render_creative_library():
    """Renders the Creative Library UI component."""
    st.header("📚 Creative Library")
    st.write("Manage your saved marketing assets.")
    
    library = get_creative_library()
    
    if not library:
        st.info("No saved items yet. Use the Agent Lab to create and save content!")
    else:
        # 1. Standard Data Management Bar
        render_data_management_bar(library, filename_prefix="creative_library")

        # Filter by agent type
        types = ["All"] + sorted(list(set([i['agent_type'] for i in library])))
        filter_type = st.selectbox("📁 Filter by Agent Type", types)
        
        display_items = library if filter_type == "All" else [i for i in library if i['agent_type'] == filter_type]
        
        # 2. Enhanced Table (for bulk actions)
        lib_df = pd.DataFrame(display_items)
        edited_lib = render_enhanced_table(lib_df, key="creative_lib_table")
        
        if 'Select' in edited_lib.columns:
            selected_items = edited_lib[edited_lib['Select'] == True]
        else:
            selected_items = pd.DataFrame()

        if not selected_items.empty:
            if st.button(f"🗑️ Delete {len(selected_items)} Selected Items", type="secondary"):
                for item_id in selected_items['id'].tolist():
                    delete_creative_item(item_id)
                st.success("Deleted!")
                st.rerun()

        st.divider()
        st.subheader("🖼️ Gallery View")
        for item in display_items:
            # Format time for the title
            created_at_str = time.strftime('%Y-%m-%d', time.localtime(item.get('created_at', 0)))
            with st.expander(f"📌 {item['agent_type']}: {item['title']} ({created_at_str})", expanded=False):
                if item['content_type'] == 'image':
                    st.image(item['body'])
                    st.caption(f"Prompt: {item['title']}")
                    st.markdown(f"[Download Image](file://{item['body']})")
                else:
                    try:
                        # Attempt to parse as JSON for pretty display
                        content = json.loads(item['body'])
                        st.json(content)
                        
                        # Simple text export
                        from io import BytesIO
                        buf = BytesIO()
                        buf.write(item['body'].encode())
                        st.download_button(
                            label="📥 Download as text",
                            data=buf.getvalue(),
                            file_name=f"{item['title'].replace(' ', '_')}.txt",
                            mime="text/plain",
                            key=f"dl_{item['id']}"
                        )
                    except:
                        # Fallback to plain text
                        st.write(item['body'])
                
                if st.button(f"🗑️ Delete Item", key=f"del_{item['id']}"):
                    delete_creative_item(item['id'])
                    st.toast("Item deleted.")
                    time.sleep(1)
                    st.rerun()

        # 3. Page Level Chat
        render_page_chat(
            "Creative Content", 
            CopywriterAgent(), 
            json.dumps(display_items, indent=2)
        )
