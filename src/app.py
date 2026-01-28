import streamlit as st
import pandas as pd
import sqlite3
import os
import sys
import asyncio
import time
import subprocess
import platform
from datetime import datetime
from dotenv import load_dotenv

try:
    import psutil
except ImportError:
    psutil = None

import json
from utils.logger_service import start_global_logging

# Add the project root to sys.path to allow imports from 'src'
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

# Force node registration
import src.nodes

# Initialize Global Logging (Singleton)
@st.cache_resource
def init_logging():
    start_global_logging()
    return True

if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

load_dotenv()

# Ensure src is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import (
    get_connection, get_pain_points, save_template, get_templates, init_db,
    clear_all_leads, delete_leads, get_campaign_analytics, get_daily_engagement,
    save_wp_site, get_wp_sites, delete_wp_site,
    save_creative_content, get_creative_library, delete_creative_item,
    create_campaign, update_campaign_step, update_campaign_pain_point,
    get_campaign, get_all_campaigns, delete_campaign, add_lead_to_campaign, get_campaign_leads, mark_contacted,
    create_dsr, update_dsr_wp_info, get_dsrs_for_campaign, get_dsr_by_lead,
    create_sequence, add_sequence_step, enroll_lead_in_sequence, get_due_enrollments, 
    get_sequence_steps, get_campaign_sequences, update_enrollment_progress,
    create_deal, get_deals, update_deal_stage, create_task, get_tasks, mark_task_completed, delete_task,
    save_scheduled_post, get_scheduled_posts, delete_scheduled_post,
    save_platform_credential, get_platform_credentials, delete_platform_credential,
    save_captcha_settings, get_captcha_settings,
    save_strategy_preset, get_strategy_presets, get_strategy_preset, delete_strategy_preset,
    create_custom_agent, get_custom_agents, get_custom_agent, delete_custom_agent,
    get_setting, save_setting,
    load_data, add_lead
)

from workflow_manager import list_workflows, load_workflow, save_workflow, delete_workflow
from workflow import run_outreach
from config import config, reload_config, update_config
from proxy_manager import proxy_manager
from ui.tabs.command import render_command_tab
from ui.tabs.outreach import render_outreach_tab
from ui.tabs.creative import render_creative_tab
from ui.tabs.tools import render_tools_tab
from ui.tabs.admin import render_admin_tab
from ui.styles import load_css

def terminate_session():
    """Stops the Streamlit server and shuts down SearXNG."""
    try:
        # 1. Stop SearXNG (Docker)
        searxng_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "searxng")
        if os.path.exists(searxng_dir):
            if platform.system() == "Windows":
                subprocess.run("docker compose down", cwd=searxng_dir, shell=True)
            else:
                 subprocess.run(["docker", "compose", "down"], cwd=searxng_dir)
                 
        print("✅ SearXNG shutdown requested.")
        
        # 2. Stop Streamlit
        st.warning("Shutting down servers... You can close this tab.")
        time.sleep(1)
        os._exit(0)
        
    except Exception as e:
        st.error(f"Error terminating session: {e}")

def process_csv_upload(uploaded_file, default_source="import", default_category="imported"):
    """Helper to process CSV uploads and add leads to DB."""
    try:
        df_import = pd.read_csv(uploaded_file)
        required_cols = ['email']
        missing = [c for c in required_cols if c.lower() not in [x.lower() for x in df_import.columns]]
        
        if missing and 'Email' not in df_import.columns and 'email' not in df_import.columns:
            st.error(f"Missing required columns: {required_cols}")
            return False
        else:
            imported_count = 0
            progress_bar = st.progress(0)
            for i, row in df_import.iterrows():
                row_data = {k.lower(): v for k, v in row.items()}
                email = row_data.get('email')
                url = row_data.get('url', '')
                source = row_data.get('source', default_source)
                category = row_data.get('category', default_category)
                industry = row_data.get('industry')
                biz_type = row_data.get('business_type')
                contact = row_data.get('contact_person')
                if email and add_lead(url, email, source=source, category=category, industry=industry, business_type=biz_type, contact_person=contact):
                    imported_count += 1
                progress_bar.progress((i + 1) / len(df_import))
            st.success(f"Successfully imported {imported_count} new leads!")
            time.sleep(1)
            st.rerun()
            return True
    except Exception as e:
        st.error(f"Import failed: {e}")
        return False

def get_system_usage():
    """Returns current CPU and RAM usage."""
    if psutil:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        return cpu, ram
    return 0, 0

@st.cache_resource
def get_auto_engine():
    from src.automation_engine import AutomationEngine
    return AutomationEngine()

async def perform_auto_llm_scan():
    """Background task to scan for free models if enabled."""
    from model_fetcher import scan_all_free_providers
    from config import config, update_config
    if not config.get('llm', {}).get('auto_scan', False): return
    last_scan = config.get('llm', {}).get('last_auto_scan', 0)
    if (time.time() - last_scan) < 43200: return
    print("[LLM-AutoScan] Starting periodic model discovery...", flush=True)
    try:
        results = await scan_all_free_providers()
        if results:
            current = config.get('llm', {}).get('router', {}).get('candidates', [])
            added = 0
            for r in results:
                if not any(c['provider'] == r['provider'] and c['model_name'] == r['model_name'] for c in current):
                    current.append(r)
                    added += 1
            if added > 0:
                print(f"[LLM-AutoScan] Success: Added {added} new free models.", flush=True)
                router = config.get('llm', {}).get('router', {}).copy()
                router['candidates'] = current
                update_config('llm', 'router', router)
            update_config('llm', 'last_auto_scan', time.time())
    except Exception as e:
        print(f"[LLM-AutoScan] Error: {e}", flush=True)

def trigger_llm_scan_bg():
    import threading
    def _run():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(perform_auto_llm_scan())
            loop.close()
        except: pass
    if not st.session_state.get('llm_auto_scan_triggered'):
        threading.Thread(target=_run, daemon=True).start()
        st.session_state['llm_auto_scan_triggered'] = True

def render_sidebar_chat():
    from ui.agent_lab_ui import render_agent_chat
    from agents import ManagerAgent
    with st.sidebar:
        st.title("🤖 AI Command")
        if 'global_chat_history' not in st.session_state:
            st.session_state['global_chat_history'] = []
        for msg in st.session_state['global_chat_history']:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        if prompt := st.chat_input("Speak to General Manager..."):
            st.session_state['global_chat_history'].append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                try:
                    agent = ManagerAgent()
                    response = agent.think(f"CONTEXT: High-level management. MISSION: {prompt}")
                    st.session_state['global_chat_history'].append({"role": "assistant", "content": response})
                    st.markdown(response)
                    st.rerun()
                except Exception as e: st.error(f"Error: {e}")

def render_top_navigation():
    """Two-tier horizontal navigation bar."""
    categories = {
        "🏠 Command": ["Dashboard", "CRM Dashboard", "Sales Pipeline", "Task Management", "Performance Reports", "Manager Console"],
        "📣 Outreach": ["Campaigns", "Lead Discovery", "Social Scheduler", "Social Pulse", "Affiliate Hub", "DSR Manager"],
        "✨ Creative": ["Designer", "Video Studio", "WordPress Manager", "Viral Engine", "Creative Library"],
        "🛠️ Tools": ["Agent Lab", "Automation Hub", "Workflow Builder", "Agent Factory", "SEO Audit", "Keyword Research", "Link Wheel Builder", "Mass Tools", "Proxy Lab", "System Monitor"],
        "⚙️ Admin": ["Settings"]
    }
    if 'current_category' not in st.session_state:
        st.session_state['current_category'] = "🏠 Command"
    
    cols = st.columns(len(categories))
    for i, cat in enumerate(categories.keys()):
        is_active = st.session_state['current_category'] == cat
        if cols[i].button(cat, key=f"cat_btn_{cat}", type="primary" if is_active else "secondary", width="stretch"):
            st.session_state['current_category'] = cat
            st.session_state['current_view'] = categories[cat][0]
            st.query_params["page"] = categories[cat][0]
            st.rerun()

    current_cat = st.session_state['current_category']
    sub_views = categories[current_cat]
    sub_cols = st.columns(len(sub_views))
    for i, view in enumerate(sub_views):
        is_active_view = st.session_state.get('current_view') == view
        if sub_cols[i].button(view, key=f"view_btn_{view}", type="primary" if is_active_view else "secondary", width="stretch"):
            if view == "Campaigns": st.session_state.pop('active_campaign_id', None)
            st.session_state['current_view'] = view
            st.query_params["page"] = view
            st.rerun()
    st.markdown("---")

def main():
    st.set_page_config(page_title="Smarketer Pro", layout="wide", page_icon="🚀")
    init_logging()
    reload_config()
    load_css()
    
    @st.cache_resource
    def run_once_init(): init_db()
    run_once_init()
    
    st.session_state['automation_engine'] = get_auto_engine()
    trigger_llm_scan_bg()
    
    if "page" in st.query_params:
        requested = st.query_params["page"]
        categories = {
            "🏠 Command": ["Dashboard", "CRM Dashboard", "Sales Pipeline", "Task Management", "Performance Reports", "Manager Console"],
            "📣 Outreach": ["Campaigns", "Lead Discovery", "Social Scheduler", "Social Pulse", "Affiliate Hub", "DSR Manager"],
            "✨ Creative": ["Designer", "Video Studio", "WordPress Manager", "Viral Engine", "Creative Library"],
            "🛠️ Tools": ["Agent Lab", "Automation Hub", "Workflow Builder", "Agent Factory", "SEO Audit", "Keyword Research", "Link Wheel Builder", "Mass Tools", "Proxy Lab", "System Monitor"],
            "⚙️ Admin": ["Settings"]
        }
        for cat, views in categories.items():
            if requested in views:
                st.session_state['current_category'] = cat
                st.session_state['current_view'] = requested
                break
    
    render_sidebar_chat()
    st.title("🚀 Smarketer Pro: CRM & Growth OS")

    stats = proxy_manager.harvest_stats
    if stats.get("is_active"):
        with st.sidebar.expander("🛰️ Harvest Progress", expanded=True):
            st.write("**Mass Proxy Harvest Active**")
            progress = stats['checked'] / stats['total'] if stats['total'] > 0 else 0
            st.progress(progress)
            h1, h2 = st.columns(2)
            h1.metric("Elite", stats.get('found_elite', 0))
            h2.metric("Std", stats.get('found_standard', 0))
            etr = stats.get('etr', 0)
            mins, secs = divmod(etr, 60)
            st.caption(f"Checked: {stats['checked']:,}/{stats['total']:,} | Est: {mins}m {secs}s")
            if st.toggle("Watch Live", value=False):
                time.sleep(1)
                st.rerun()
    
    render_top_navigation()
    
    category = st.session_state.get('current_category', "🏠 Command")
    if category == "🏠 Command": render_command_tab()
    elif category == "📣 Outreach": render_outreach_tab()
    elif category == "✨ Creative": render_creative_tab()
    elif category == "🛠️ Tools": render_tools_tab()
    elif category == "⚙️ Admin": render_admin_tab()
    else: st.error(f"Unknown Category: {category}")

if __name__ == '__main__':
    try: main()
    except Exception as e:
        if type(e).__name__ in ["RerunException", "StopException"]: raise e
        import traceback
        msg = f"CRITICAL: App crashed: {e}\n{traceback.format_exc()}"
        print(msg, file=sys.stderr)
        try:
            with open("logs/crash.log", "a") as f: f.write(f"\n[{datetime.now()}] {msg}\n")
        except: pass
