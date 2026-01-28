import streamlit as st
import sys
import os
import importlib

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

st.set_page_config(page_title="Debug Import")
st.write("### Agent Import Diagnostic")

# List based on __init__.py
modules_to_test = [
    "agents.base",
    "agents.reviewer",
    "agents.syntax",
    "agents.ux",
    "agents.researcher",
    "agents.qualifier",
    "agents.copywriter",
    "agents.manager",
    "agents.designer",
    "agents.creative",
    "agents.wordpress",
    "agents.pm",
    "agents.linkedin",
    "agents.seo_agent",
    "agents.video_agent",
    "agents.influencer_agent",
    "agents.social_listener",
    "agents.image_agent", 
    "agents.contact_form_agent",
    "agents.data_cleaner",
    "agents.sales_analyzer",
    "agents.knowledge_architect",
    "agents.prompt_expert",
    "agents.summarizer",
    "agents.meet_scribe"
]

for mod in modules_to_test:
    try:
        st.write(f"Testing {mod}...")
        importlib.import_module(mod)
        st.write(f"**{mod}**: OK ✅")
    except Exception as e:
        st.error(f"**{mod}**: FAILED ❌ ({e})")
    except KeyboardInterrupt:
        st.error(f"**{mod}**: TIMEOUT/HANG 🛑")
        break

st.success("Test Complete")
