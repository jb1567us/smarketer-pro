
import streamlit as st
import sys
import os

# Mock streamlit functions
class MockSt:
    def __init__(self):
        self.session_state = {"app_mode": "B2B"}
    def columns(self, spec): return [MockCol() for _ in range(len(spec) if isinstance(spec, list) else spec)]
    def title(self, *args, **kwargs): pass
    def caption(self, *args, **kwargs): pass
    def markdown(self, *args, **kwargs): pass
    def divider(self, *args, **kwargs): pass
    def metric(self, *args, **kwargs): pass
    def subheader(self, *args, **kwargs): pass
    def button(self, *args, **kwargs): return False
    def info(self, *args, **kwargs): pass
    def rerun(self): pass

class MockCol:
    def __enter__(self): return self
    def __exit__(self, exc_type, exc_val, exc_tb): pass
    def title(self, *args, **kwargs): pass
    def caption(self, *args, **kwargs): pass
    def markdown(self, *args, **kwargs): pass
    def metric(self, *args, **kwargs): pass
    def info(self, *args, **kwargs): pass
    def button(self, *args, **kwargs): return False

# Patch streamlit
import streamlit
st.columns = MockSt().columns
st.title = MockSt().title
st.caption = MockSt().caption
st.markdown = MockSt().markdown
st.divider = MockSt().divider
st.metric = MockSt().metric
st.subheader = MockSt().subheader
st.button = MockSt().button
st.info = MockSt().info
st.rerun = MockSt().rerun
st.session_state = MockSt().session_state

# Import and run
try:
    sys.path.append(os.path.abspath("src"))
    from ui.dashboard_ui import render_dashboard
    print("Import successful.")
    render_dashboard()
    print("Render successful.")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

