import streamlit as st
import time
import pandas as pd

def render_step_progress(steps, current_step_idx):
    """Renders a horizontal stepper progress bar."""
    
    # Calculate progress percentage
    progress = int((current_step_idx + 1) / len(steps) * 100)
    
    st.markdown(f"""
    <div style="margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px; color: var(--text-color); opacity: 0.6; font-size: 0.9rem; font-weight: 500;">
            <span>Step {current_step_idx + 1} of {len(steps)}</span>
            <span>{progress}% Completed</span>
        </div>
        <div style="height: 8px; width: 100%; background-color: rgba(128, 128, 128, 0.2); border-radius: 4px; overflow: hidden;">
            <div style="height: 100%; width: {progress}%; background-color: var(--primary-color); border-radius: 4px; transition: width 0.5s ease;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    cols = st.columns(len(steps))
    for i, step in enumerate(steps):
        is_active = i == current_step_idx
        is_completed = i < current_step_idx
        
        color = "var(--primary-color)" if is_active or is_completed else "var(--text-color)"
        weight = "700" if is_active else "400"
        opacity = "1" if is_active or is_completed else "0.5"
        
        with cols[i]:
            st.markdown(f"<div style='text-align: center; color: {color}; font-weight: {weight}; opacity: {opacity}; font-size: 0.85rem;'>{step}</div>", unsafe_allow_html=True)
    
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
        st.markdown(f"<p style='color: var(--text-color); opacity: 0.6; font-size: 1.1rem; margin-top: -10px; margin-bottom: 30px;'>{subtitle}</p>", unsafe_allow_html=True)

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
            width="stretch"
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
                width="stretch"
            )
        except Exception:
            st.button("📊 Export CSV", disabled=True, width="stretch")

    with col3:
        if on_import:
            uploaded_file = st.file_uploader(
                "📥 Import Data", 
                type=['json', 'csv'], 
                label_visibility="collapsed",
                help="Upload a JSON or CSV file to import data."
            )
            if uploaded_file is not None:
                if st.button("Apply Import", width="stretch"):
                    on_import(uploaded_file)
        else:
            st.button("📥 Import", disabled=True, width="stretch")

    with col4:
        if on_delete:
            if st.button("🗑️ Delete Selected", type="secondary", width="stretch"):
                on_delete()
        else:
            st.button("🗑️ Delete", disabled=True, width="stretch")

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
        width="stretch"
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

def confirm_action(label, prompt, on_confirm, key=None, type="secondary"):
    """Standardized confirmation popover for destructive or important actions."""
    with st.popover(label, width="stretch"):
        st.warning(prompt)
        if st.button("Confirm ✅", key=f"conf_{key or label}", type="primary", width="stretch"):
            on_confirm()
            st.rerun()

def safe_action_wrapper(func, success_message="Action completed!"):
    """Friendly error wrapper for back-end operations."""
    try:
        result = func()
        if success_message:
            st.toast(success_message, icon="✅")
        return result
    except Exception as e:
        st.error(f"⚠️ Operation Failed: We encountered an issue while processing your request.")
        with st.expander("Show Technical Details"):
            st.code(str(e))
        return None

def render_job_controls(job_name, is_running, on_start, on_stop, progress=None, status_text=None):
    """Standardized Start/Stop controls with progress feedback."""
    cols = st.columns([1, 3])
    with cols[0]:
        if is_running:
            if st.button(f"🛑 Stop {job_name}", key=f"stop_{job_name}", type="primary", width="stretch"):
                if on_stop: on_stop()
                st.rerun()
        else:
            if st.button(f"▶️ Start {job_name}", key=f"start_{job_name}", type="primary", width="stretch"):
                if on_start: on_start()
                st.rerun()
    
    with cols[1]:
        if is_running:
            if progress is not None:
                st.progress(progress, text=status_text or f"{job_name} is in progress...")
            else:
                st.info(status_text or f"🔄 {job_name} is running...")
        else:
            st.write(f"Idle - Ready to start {job_name.lower()}.")
