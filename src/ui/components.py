import streamlit as st

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
