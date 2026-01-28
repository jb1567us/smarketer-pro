import streamlit as st
import time
import sys
import os

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(page_title="Debug Mode")
st.write("### 1. Streamlit Initialized")

try:
    from config import config, reload_config
    reload_config()
    st.write("### 2. Config Loaded ✅")
except Exception as e:
    st.error(f"Config Failed: {e}")

try:
    from database import init_db
    init_db()
    st.write("### 3. DB Initialized ✅")
except Exception as e:
    st.error(f"DB Failed: {e}")

try:
    st.write("### 4. Importing Agents...")
    from agents import ManagerAgent
    st.write("### 5. ManagerAgent Imported ✅")
except Exception as e:
    st.error(f"Agent Import Failed: {e}")

st.success("Startup Debug Complete")
