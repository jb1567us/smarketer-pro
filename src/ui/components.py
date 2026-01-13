import streamlit as st
import time
import pandas as pd

def render_step_progress(steps, current_step_idx):
    """Renders a horizontal stepper progress bar."""
    
    # Calculate progress percentage
    progress = int((current_step_idx + 1) / len(steps) * 100)
    
    st.markdown(f"""
    <div style="margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px; color: #6b7280; font-size: 0.9rem; font-weight: 500;">
            <span>Step {current_step_idx + 1} of {len(steps)}</span>
            <span>{progress}% Completed</span>
        </div>
        <div style="height: 8px; width: 100%; background-color: #e5e7eb; border-radius: 4px; overflow: hidden;">
            <div style="height: 100%; width: {progress}%; background-color: #2563eb; border-radius: 4px; transition: width 0.5s ease;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    cols = st.columns(len(steps))
    for i, step in enumerate(steps):
        is_active = i == current_step_idx
        is_completed = i < current_step_idx
        
        color = "#2563eb" if is_active or is_completed else "#9ca3af"
        weight = "700" if is_active else "400"
        
        with cols[i]:
            st.markdown(f"<div style='text-align: center; color: {color}; font-weight: {weight}; font-size: 0.85rem;'>{step}</div>", unsafe_allow_html=True)
    
    st.markdown("---")

def card(content_func, title=None, key=None):
    """Wraps content in a styled card."""
    with st.container():
        st.markdown(f'<div class="css-card">', unsafe_allow_html=True)
        if title:
            st.markdown(f"### {title}")
        content_func()
        st.markdown('</div>', unsafe_allow_html=True)

def premium_header(title, subtitle=None):
    st.markdown(f"# {title}")
    if subtitle:
        st.markdown(f"<p style='color: #6b7280; font-size: 1.1rem; margin-top: -10px; margin-bottom: 30px;'>{subtitle}</p>", unsafe_allow_html=True)

def render_data_management_bar(data, filename_prefix="export", on_delete=None, on_import=None):
    """
    Renders a standardized bar for exporting, importing, and deleting data.
    """
    import json
    import pandas as pd
    from io import BytesIO

    col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
    
    with col1:
        # Export JSON
        json_str = json.dumps(data, indent=2)
        st.download_button(
            label="📤 Export JSON",
            data=json_str,
            file_name=f"{filename_prefix}_{int(time.time())}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col2:
        # Export CSV
        try:
            df = pd.DataFrame(data)
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📊 Export CSV",
                data=csv,
                file_name=f"{filename_prefix}_{int(time.time())}.csv",
                mime="text/csv",
                use_container_width=True
            )
        except Exception:
            st.button("📊 Export CSV", disabled=True, use_container_width=True)

    with col3:
        if on_import:
            uploaded_file = st.file_uploader("📥 Import Data", type=['json', 'csv'], label_visibility="collapsed")
            if uploaded_file is not None:
                if st.button("Apply Import", use_container_width=True):
                    on_import(uploaded_file)
        else:
            st.button("📥 Import", disabled=True, use_container_width=True)

    with col4:
        if on_delete:
            if st.button("🗑️ Delete Selected", type="secondary", use_container_width=True):
                on_delete()
        else:
            st.button("🗑️ Delete", disabled=True, use_container_width=True)

def render_enhanced_table(df, key, selection_key=None):
    """
    Renders a table with checkboxes for selection and a 'Select All' toggle.
    """
    if df.empty:
        st.info("No data available.")
        return pd.DataFrame()

    # Add Select checkbox if not present
    if 'Select' not in df.columns:
        df.insert(0, 'Select', False)
    
    # Select All Toggle
    col1, col2 = st.columns([1, 4])
    with col1:
        # Detect if 'Select All' state exists, default to False
        all_key = f"all_state_{key}"
        if all_key not in st.session_state:
            st.session_state[all_key] = False
            
        select_all = st.checkbox("Select All", key=f"cb_all_{key}", value=st.session_state[all_key])
        
        # If the master checkbox changed, update the dataframe and clear editor state
        if select_all != st.session_state[all_key]:
            df['Select'] = select_all
            st.session_state[all_key] = select_all
            # Clear data_editor's internal state to force refresh from the new df
            if key in st.session_state:
                del st.session_state[key]
            st.rerun()

    # Use data_editor for selection
    edited_df = st.data_editor(
        df,
        key=key,
        hide_index=True,
        column_config={
            "Select": st.column_config.CheckboxColumn(
                "Select",
                help="Select items for bulk action",
                default=False,
            )
        },
        disabled=[c for c in df.columns if c != 'Select'],
        use_container_width=True
    )
    
    return edited_df

def render_page_chat(context_description, agent_instance, context_data):
    """
    Renders a standard chat floating box or expander for continuous tweaking.
    """
    from ui.agent_lab_ui import render_agent_chat
    
    with st.expander(f"💬 AI Assistant: Tweak {context_description}", expanded=False):
        st.info(f"Chat with the AI to refine your {context_description.lower()}.")
        render_agent_chat(
            response_key=f"page_chat_resp_{context_description.replace(' ', '_')}",
            agent_instance=agent_instance,
            context_key=f"page_chat_ctx_{context_description.replace(' ', '_')}"
        )
        # Seed the context if not present
        ctx_key = f"page_chat_ctx_{context_description.replace(' ', '_')}"
        if ctx_key not in st.session_state:
            st.session_state[ctx_key] = context_data
