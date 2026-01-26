import streamlit as st
import pandas as pd
import sqlite3
import os
import sys
import os

# Add the project root to sys.path to allow imports from 'src'
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

# Force node registration
import src.nodes

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

# Initialize Global Logging (Singleton)
# Using cache_resource ensures this runs only once per server lifetime (mostly)
@st.cache_resource
def init_logging():
    start_global_logging()
    return True


# init_logging call moved to main()

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
    load_data
)
from workflow_manager import list_workflows, load_workflow, save_workflow, delete_workflow
from workflow import run_outreach
from campaign_manager import start_campaign_step_research, start_campaign_step_copy, start_campaign_step_send, refine_campaign_step_research
from dsr_manager import DSRManager
from ui.agent_lab_ui import render_agent_lab, render_tuning_dialog, render_agent_chat
from ui.affiliate_ui import render_affiliate_ui
from ui.components import render_enhanced_table, render_data_management_bar, render_page_chat
from cadence_manager import CadenceManager
from enrichment_manager import EnrichmentManager
from automation_engine import AutomationEngine
from mailer import Mailer
from ui.reports_ui import render_reports_page
from ui.settings_ui import render_settings_page
from ui.campaign_ui import render_campaign_page
from ui.mass_tools_ui import render_mass_tools_page
from ui.social_hub_ui import render_social_scheduler_page, render_social_pulse_page
from ui.crm_ui import render_crm_dashboard
from ui.video_ui import render_video_studio
from ui.designer_ui import render_designer_page
from ui.dashboard_ui import render_dashboard
from ui.account_creator_ui import render_account_creator_ui
from ui.agency_ui import render_agency_ui
from ui.pm_ui import render_pm_ui
from ui.dsr_ui import render_dsr_page
from ui.hosting_ui import render_hosting_dashboard
from ui.manager_ui import render_manager_ui
from model_fetcher import fetch_models_for_provider, scan_all_free_providers
from config import config, reload_config, update_config
from proxy_manager import proxy_manager
from agents import (
    ResearcherAgent, QualifierAgent, CopywriterAgent, ReviewerAgent, 
    GraphicsDesignerAgent, WordPressAgent, ManagerAgent, ProductManagerAgent,
    SyntaxAgent, UXAgent, SEOExpertAgent, InfluencerAgent, SocialListeningAgent, LinkedInAgent
)
from agents.custom_agent import CustomAgent

# Force reload config on every run to pick up external changes

# reload_config call moved to main()


# st.set_page_config call moved to main()

# Import UI Styles
from ui.styles import load_css

# load_css call moved to main()




def terminate_session():
    """Stops the Streamlit server and shuts down SearXNG."""
    try:
        # 1. Stop SearXNG (Docker)
        searxng_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "searxng")
        if os.path.exists(searxng_dir):
            if platform.system() == "Windows":
                # Check if docker-compose or docker compose
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

    except Exception as e:
        st.error(f"Error terminating session: {e}")

# load_data moved to database.py


def process_csv_upload(uploaded_file, default_source="import", default_category="imported"):
    """Helper to process CSV uploads and add leads to DB."""
    try:
        df_import = pd.read_csv(uploaded_file)
        # Basic validation
        required_cols = ['email'] # minimal requirement
        missing = [c for c in required_cols if c.lower() not in [x.lower() for x in df_import.columns]]
        
        if missing and 'Email' not in df_import.columns and 'email' not in df_import.columns:
            st.error(f"Missing required columns: {required_cols}")
            return False
        else:
            # Normalized logic
            imported_count = 0
            progress_bar = st.progress(0)
            
            for i, row in df_import.iterrows():
                # Normalize keys
                row_data = {k.lower(): v for k, v in row.items()}
                
                email = row_data.get('email')
                url = row_data.get('url', '')
                source = row_data.get('source', default_source)
                category = row_data.get('category', default_category)
                
                # Optional fields
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
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    return cpu, ram

# Automation Engine (Singleton Service)
@st.cache_resource
def get_auto_engine():
    from src.automation_engine import AutomationEngine
    return AutomationEngine()

async def perform_auto_llm_scan():
    """Background task to scan for free models if enabled."""
    # Local import to avoid circular dependencies
    from model_fetcher import scan_all_free_providers
    from config import config, update_config
    
    if not config.get('llm', {}).get('auto_scan', False):
        return

    # Check last scan time (12 hour cooldown)
    last_scan = config.get('llm', {}).get('last_auto_scan', 0)
    current_time = time.time()
    
    if (current_time - last_scan) < 43200: # 12 hours
        return
        
    print("[LLM-AutoScan] Starting periodic model discovery...", flush=True)
    try:
        results = await scan_all_free_providers()
        if results:
            current_candidates = config.get('llm', {}).get('router', {}).get('candidates', [])
            
            # Merge logic
            new_candidates = current_candidates.copy()
            added = 0
            for r in results:
                if not any(c['provider'] == r['provider'] and c['model_name'] == r['model_name'] for c in new_candidates):
                    new_candidates.append(r)
                    added += 1
            
            if added > 0:
                print(f"[LLM-AutoScan] Success: Added {added} new free models to router.", flush=True)
                router_config = config.get('llm', {}).get('router', {}).copy()
                router_config['candidates'] = new_candidates
                update_config('llm', 'router', router_config)
            
            # Always update timestamp to avoid retry loops on failure if it's partially working
            update_config('llm', 'last_auto_scan', current_time)
        
    except Exception as e:
        print(f"[LLM-AutoScan] Error during startup scan: {e}", flush=True)

def trigger_llm_scan_bg():
    """Triggers the scan in a background thread to avoid blocking startup UI."""
    import threading
    def _run():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(perform_auto_llm_scan())
            loop.close()
        except Exception as e:
            print(f"[LLM-AutoScan] Thread failed: {e}", flush=True)
    
    # Run once per process life
    if not st.session_state.get('llm_auto_scan_triggered'):
        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        st.session_state['llm_auto_scan_triggered'] = True

def render_sidebar_chat():
    """Persistent AI Command Center in the sidebar."""
    with st.sidebar:
        st.title("🤖 Assistant")
        st.caption("AI Command Center")
        
        # Initialize History
        if 'global_chat_history' not in st.session_state:
            st.session_state['global_chat_history'] = []
            
        # Display History
        for msg in st.session_state['global_chat_history']:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
        # Chat Input
        if prompt := st.chat_input("Ask me anything...", key="sidebar_chat_input"):
            st.session_state['global_chat_history'].append({"role": "user", "content": prompt})
            # Force refresh to show user message immediately
            st.rerun()

    # Process response in a separate block if last message is from user
    # to avoid the "chat_input inside with st.sidebar" restriction if it exists
    if st.session_state.get('global_chat_history') and st.session_state['global_chat_history'][-1]['role'] == 'user':
        last_prompt = st.session_state['global_chat_history'][-1]['content']
        with st.sidebar:
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        from agents import ManagerAgent
                        manager = ManagerAgent()
                        response = manager.think(last_prompt)
                        st.session_state['global_chat_history'].append({"role": "assistant", "content": response})
                        st.markdown(response)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

def render_top_navigation():
    """Two-tier horizontal navigation bar."""
    
    # 1. Categories
    categories = {
        "🏠 Command": ["Dashboard", "CRM Dashboard", "Performance Reports", "Manager Console"],
        "📣 Outreach": ["Campaigns", "Lead Discovery", "Social Scheduler", "Social Pulse", "Affiliate Hub", "DSR Manager"],
        "✨ Creative": ["Designer", "Video Studio", "WordPress Manager"],
        "🛠️ Tools": ["Agent Lab", "Account Creator", "Hosting Dashboard", "Proxy Lab", "Product Lab", "System Monitor"],
        "⚙️ Admin": ["Settings"]
    }

    # Initialize current category if not set
    if 'current_category' not in st.session_state:
        st.session_state['current_category'] = "🏠 Command"

    st.markdown("---")
    cat_cols = st.columns(len(categories))
    for i, cat in enumerate(categories.keys()):
        with cat_cols[i]:
            is_active = st.session_state['current_category'] == cat
            btn_type = "primary" if is_active else "secondary"
            if st.button(cat, key=f"cat_btn_{cat}", width="stretch", type=btn_type):
                st.session_state['current_category'] = cat
                # Default to first view in category when switching
                st.session_state['current_view'] = categories[cat][0]
                st.query_params["page"] = categories[cat][0]
                st.rerun()

    # 2. Sub-Views (Functional)
    current_cat = st.session_state['current_category']
    sub_views = categories[current_cat]
    
    sub_cols = st.columns(len(sub_views))
    for i, view in enumerate(sub_views):
        with sub_cols[i]:
            is_active_view = st.session_state.get('current_view') == view
            # Use small text or different style for sub-nav
            if st.button(view, key=f"view_btn_{view}", width="stretch"):
                if view == "Campaigns":
                    st.session_state.pop('active_campaign_id', None)
                st.session_state['current_view'] = view
                st.query_params["page"] = view
                st.rerun()
    st.markdown("---")

def main():
    st.set_page_config(page_title="Smarketer Pro", layout="wide", page_icon="🚀")
    init_logging()
    reload_config()
    load_css()
    init_db()
    
    st.session_state['automation_engine'] = get_auto_engine()
    trigger_llm_scan_bg()
    
    # Trigger background proxy check (once per session)
    if not st.session_state.get('proxy_startup_checked'):
        # Use 1 hour window for startup to ensure fresh session
        proxy_manager.ensure_fresh_bg(max_age_hours=1)
        st.session_state['proxy_startup_checked'] = True
    
    # 0. Sync URL parameters with session state
    if "page" in st.query_params:
        requested_page = st.query_params["page"]
        
        # 1. Categories Mapping (Reverse lookup)
        categories = {
            "🏠 Command": ["Dashboard", "CRM Dashboard", "Performance Reports", "Manager Console"],
            "📣 Outreach": ["Campaigns", "Lead Discovery", "Social Scheduler", "Social Pulse", "Affiliate Hub", "DSR Manager"],
            "✨ Creative": ["Designer", "Video Studio", "WordPress Manager"],
            "🛠️ Tools": ["Agent Lab", "Account Creator", "Hosting Dashboard", "Proxy Lab", "Product Lab", "System Monitor"],
            "⚙️ Admin": ["Settings"]
        }

        # Check if page exists and set category
        for cat, views in categories.items():
            if requested_page in views:
                st.session_state['current_category'] = cat
                st.session_state['current_view'] = requested_page
                break
    
    # 1. Sidebar Intelligence (Persistent)
    render_sidebar_chat()
    
    st.title("🚀 Smarketer Pro: CRM & Growth OS")

    # === GLOBAL PROXY HARVEST PROGRESS (NON-BLOCKING) ===
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
            
            # Non-blocking refresh: Only rerun if user opts in
            if st.toggle("Watch Live", value=False, help="Enable auto-refresh to see progress in real-time."):
                time.sleep(1)
                st.rerun()
    
    # 2. Top Navigation
    render_top_navigation()
    
    choice = st.session_state.get('current_view', 'Dashboard')
    if choice.startswith("---"):
        st.warning("Please select a valid functional page.")
        return



    if choice == "Dashboard":
        render_dashboard()

    elif choice == "CRM Dashboard":
        render_crm_dashboard()

    elif choice == "Performance Reports":
        render_reports_page()

    elif choice == "Manager Console":
        render_manager_ui()

    elif choice == "Campaigns":
        render_campaign_page()

    elif choice == "Lead Discovery":
        render_mass_tools_page()

    elif choice == "Affiliate Hub":
        render_affiliate_ui()

    elif choice == "DSR Manager":
        render_dsr_page()

    elif choice == "Video Studio":
        render_video_studio()

    elif choice == "Designer":
        render_designer_page()

    elif choice == "Social Scheduler":
        render_social_scheduler_page()

    elif choice == "Social Pulse":
        render_social_pulse_page()

    elif choice == "WordPress Manager":
        # Using hosting dashboard as it contains WP management logic
        render_hosting_dashboard()

    elif choice == "Agent Lab":
        render_agent_lab()

    elif choice == "Account Creator":
        render_account_creator_ui()

    elif choice == "System Monitor":
        st.header("💻 System Monitor")
        st.caption("Live view of backend processes, agent thoughts, and system logs.")
        
        # CPU/RAM Stats
        if psutil:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            c1, c2 = st.columns(2)
            c1.metric("CPU Usage", f"{cpu}%")
            
            # RAM Color Logic
            ram_delta_color = "normal"
            if ram > 85: ram_delta_color = "inverse"
            c2.metric("RAM Usage", f"{ram}%", delta_color=ram_delta_color)
            if ram > 90:
                st.error("⚠️ High Memory Usage! Performance may degrade.")

        st.divider()
        st.subheader("📜 Live Engine Logs")
        
        # Log Reader
        log_path = os.path.join(project_root, "logs", "engine.log")
        
        col_ctrl, col_view = st.columns([1, 4])
        with col_ctrl:
            auto_refresh = st.toggle("Auto-Refresh", value=True)
            if st.button("🗑️ Clear Logs"):
                open(log_path, 'w').close()
                st.success("Logs cleared.")
                st.rerun()
            
            lines_to_show = st.select_slider("Lines", options=[50, 100, 200, 500, 1000], value=100)
            
        with col_view:
            log_container = st.empty()
            
            # Simple tail implementation
            try:
                if os.path.exists(log_path):
                    with open(log_path, 'r', encoding='utf-8') as f:
                        # Improved: Read last N lines effectively
                         # For small files traverse; for large files seek
                        lines = f.readlines()
                        last_n = lines[-lines_to_show:]
                        log_text = "".join(last_n)
                        
                        st.code(log_text, language="log")
                else:
                    st.info("Log file not found yet (waiting for startup...)")
            except Exception as e:
                st.error(f"Error reading log: {e}")
        
        if auto_refresh:
            time.sleep(2)
            st.rerun()

    elif choice == "Hosting Dashboard":
        render_hosting_dashboard()


    elif choice == "Product Lab":
        render_pm_ui()

    elif choice == "Settings":
        render_settings_page()

    elif choice == "Analytics":
        st.header("📊 Campaign Analytics")
        # ... (rest of Analytics code)
        st.caption("Insights from your outreach campaigns.")
        
        analytics = get_campaign_analytics()
        
        # Top-level metrics
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Leads Contacted", analytics['leads_contacted'])
        m2.metric("Emails Sent", analytics['sent'])
        m3.metric("Opened", analytics['open'])
        m4.metric("Clicked", analytics['click'])
        
        st.divider()
        
        # Funnel Chart
        st.subheader("Conversion Funnel")
        funnel_data = {
            "Stage": ["Sent", "Opened", "Clicked"],
            "Count": [analytics['sent'], analytics['open'], analytics['click']]
        }
        st.bar_chart(funnel_data, x="Stage", y="Count")
        
        # Engagement Timeline
        st.subheader(" Engagement Over Time (Last 30 Days)")
        daily_data = get_daily_engagement(days=30)
        
        # Transform for chart (list of dicts)
        chart_rows = []
        for day, metrics in daily_data.items():
            row = {'Day': day, 'Sent': metrics['sent'], 'Opens': metrics['open'], 'Clicks': metrics['click']}
            chart_rows.append(row)
            
        if chart_rows:
            st.line_chart(chart_rows, x="Day", y=["Sent", "Opens", "Clicks"])
        else:
            st.info("No activity recorded yet.")

        st.divider()
        st.subheader("💡 AI Optimization Insights")
        
        # Simulated Campaign Data for Optimization
        col_opt1, col_opt2 = st.columns(2)
        with col_opt1:
            st.info("Analyzing Campaign: **'SaaS Founders Outreach Q3'**")
            current_stats = {"open_rate": 0.18, "click_rate": 0.02} # Simulated low performance
            st.metric("Open Rate", "18%", "-7% vs avg", delta_color="inverse")
            st.metric("Click Rate", "2.0%", "-3% vs avg", delta_color="inverse")
            
        with col_opt2:
            if st.button("✨ Auto-Optimize Campaign"):
                # agent = CopywriterAgent() # Using global
                agent = CopywriterAgent()
                
                # Mock current copy
                current_copy = {
                    "subject": "Quick question",
                    "body": "Hi there, I saw your profile and thought..."
                }
                
                with st.spinner("AI is analyzing performance and rewriting copy..."):
                    # Call the optimization method
                    res = agent.optimize_campaign(current_copy, current_stats)
                    
                    st.success("Optimization Complete!")
                    st.json(res)
                    if "optimized_variants" in res:
                        st.subheader("Suggested Variants:")
                        for v in res['optimized_variants']:
                            st.code(v, language="text")

        # 3. Page Level Chat
        render_page_chat(
            "Campaign Analytics", 
            ManagerAgent(), 
            json.dumps(analytics, indent=2)
        )

    elif choice == "CRM Dashboard":
        render_crm_dashboard()

    elif choice == "Pipeline (Deals)":
        st.header("📂 Sales Pipeline")
        
        # CSS Fix for stage headers wrapping
        st.markdown("""
            <style>
            [data-testid="stMetricValue"] {
                font-size: 1.8rem;
            }
            .stMarkdown h3 {
                white-space: nowrap;
                font-size: 1.1rem !important;
            }
            </style>
        """, unsafe_allow_html=True)

        tab_kanban, tab_table = st.tabs(["📋 Kanban Board", "📑 Table View"])

        with tab_kanban:
            # ➕ New Deal Section
            with st.expander("➕ Create New Deal", expanded=False):
                with st.form("new_deal_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        d_title = st.text_input("Deal Title", placeholder="e.g. Enterprise License")
                        d_val = st.number_input("Value ($)", min_value=0.0, step=100.0)
                    with col2:
                        # Fetch leads to associate
                        leads = get_leads_by_status("new") + get_leads_by_status("contacted")
                        lead_options = {f"{l['company_name'] or 'Unknown'} ({l['email']})": l['id'] for l in leads}
                        target_lead = st.selectbox("Associate Lead", list(lead_options.keys()))
                    
                    if st.form_submit_button("Create Deal", type="primary"):
                        if d_title and target_lead:
                            deal_id = create_deal(lead_options[target_lead], d_title, d_val)
                            st.success(f"Deal created! (ID: {deal_id})")
                            time.sleep(1)
                            st.rerun()

            st.divider()
            deals = get_deals()
            stages = ["Discovery", "Qualification", "Proposal", "Negotiation", "Closed Won", "Closed Lost"]
            cols = st.columns(len(stages))
            for i, stage in enumerate(stages):
                with cols[i]:
                    st.markdown(f"### {stage}")
                    for d in [d for d in deals if d['stage'] == stage]:
                        with st.expander(f"{d['title']}", expanded=True):
                            st.write(f"${d['value']:,.0f}")
                            st.caption(f"{d['company_name']}")
                            new_s = st.selectbox("Stage", stages, index=stages.index(stage), key=f"s_{d['id']}")
                            if new_s != stage:
                                update_deal_stage(d['id'], new_s, 50)
                                st.rerun()

        with tab_table:
            st.subheader("Manage Deals")
            deals = get_deals()
            if deals:
                deals_df = pd.DataFrame(deals)
                # 1. Standard Data Management Bar
                render_data_management_bar(deals, filename_prefix="pipeline_deals")

                # 2. Enhanced Table
                edited_deals = render_enhanced_table(deals_df, key="pipeline_deals_table")
                
                selected_deals = edited_deals[edited_deals['Select'] == True]
                if not selected_deals.empty:
                    if st.button(f"🗑️ Delete {len(selected_deals)} Selected Deals", type="secondary"):
                        delete_deals_bulk(selected_deals['id'].tolist())
                        st.success("Deleted!")
                        st.rerun()
            else:
                st.info("No deals in pipeline.")

        # 3. Page Level Chat
        render_page_chat(
            "Sales Pipeline", 
            ManagerAgent(), 
            json.dumps(get_deals(), indent=2)
        )

    elif choice == "Proxy Lab":
        st.header("🌐 Proxy Harvester Lab")
        st.caption("Advanced ScrapeBox-style proxy management and elite harvesting.")

        # Dashboard Stats
        col1, col2, col3, col4 = st.columns(4)
        # Fetching counts from DB for accuracy
        from database import get_best_proxies
        elites = len(get_best_proxies(limit=1000, min_anonymity='elite'))
        standards = len(get_best_proxies(limit=1000, min_anonymity='standard'))
        
        col1.metric("Active Elite", elites)
        col2.metric("Active Standard", standards)
        col3.metric("Bad Blocked", len(proxy_manager.bad_proxies))
        col4.metric("Usage", "Enabled" if proxy_manager.enabled else "Disabled")
        
        st.divider()
        
        col_main, col_side = st.columns([2, 1])
        
        with col_main:
            st.subheader("Proxy Pool (Active)")
            from database import get_best_proxies
            all_best = get_best_proxies(limit=1000)
            if all_best:
                proxy_df = pd.DataFrame(all_best)
                # Ensure correct columns displayed
                display_cols = ["address", "anonymity", "latency"]
                existing_cols = [c for c in display_cols if c in proxy_df.columns]
                st.dataframe(proxy_df[existing_cols], hide_index=True, width="stretch")
            else:
                st.warning("No active proxies found. Start a harvest to populate the pool.")
            
        with col_side:
            st.subheader("Control Panel")
            
            # Concurrency Slider
            curr_conc = config.get("proxies", {}).get("harvest_concurrency", 50)
            new_conc = st.slider("Harvest Concurrency", min_value=1, max_value=400, value=curr_conc, step=10, help="Max concurrent connections for proxy harvesting.")
            
            if new_conc != curr_conc:
                update_config("proxies", "harvest_concurrency", new_conc)
                st.toast(f"Concurrency updated to {new_conc}!")
                time.sleep(0.5)
                st.rerun()
            # Check state change
            new_state = st.toggle("Enable Upstream Proxies", value=proxy_manager.enabled, key="proxy_toggle")
            
            if new_state != proxy_manager.enabled:
                if new_state:
                    with st.spinner("Enabling proxies and refreshing... (Restarts SearXNG)"):
                        success, cx_msg = asyncio.run(proxy_manager.enable_proxies())
                        if success: 
                            st.success(cx_msg)
                            time.sleep(2)
                            st.rerun()
                        else: st.error(cx_msg)
                else:
                    with st.spinner("Disabling proxies... (Restarts SearXNG)"):
                        success, cx_msg = asyncio.run(proxy_manager.disable_proxies())
                        if success: 
                            st.success(cx_msg)
                            time.sleep(2)
                            st.rerun()
                        else: st.error(cx_msg)
            
            st.divider()

            if st.button("🚀 Trigger Mass Harvest", width="stretch", type="primary"):
                success, msg = proxy_manager.start_harvest_bg()
                if success:
                    st.success("🛰️ Background harvest initiated. Observe progress above.")
                    time.sleep(1)
                    st.rerun()
                else: 
                    st.error(msg)
            
            if st.button("🧹 Clear Bad Proxies", width="stretch"):
                proxy_manager.bad_proxies.clear()
                st.success("Bad proxy list cleared.")
                st.rerun()

            with st.expander("📥 Import Custom Proxies"):
                import_text = st.text_area("Paste Proxy List (IP:Port)", height=100, placeholder="192.168.1.1:8080\n10.0.0.1:3128")
                if st.button("Import Peers"):
                    if import_text:
                        count, new_p = asyncio.run(proxy_manager.import_proxies(import_text))
                        st.success(f"Imported {count} unique proxies.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.warning("Paste some proxies first!")

            st.divider()
            
            st.markdown("#### 🔗 SearXNG Integration")
            if st.button("💉 Inject Proxies into SearXNG", width="stretch", help="Updates SearXNG settings.yml and restarts the container."):
                if not proxy_manager.proxies:
                    st.error("No proxies to inject! Harvest some first.")
                else:
                    with st.spinner("Injecting proxies and restarting SearXNG Docker container..."):
                        success, cx_msg = asyncio.run(proxy_manager.update_searxng_config())
                        if success:
                            st.success(cx_msg)
                        else:
                            st.error(cx_msg)
            
            st.divider()
            st.info("The Proxy Harvester automatically performs L3 anonymity checks and rotates every request by default.")

    elif choice == "Video Studio":
        render_video_studio()

    elif choice == "DSR Manager":
        render_dsr_page()



    elif choice == "Reports":
        render_reports_page()

    elif choice == "Account Creator":
        render_account_creator_ui()

    elif choice == "System Monitor":
        st.header("💻 System Monitor")
        st.caption("Live view of backend processes, agent thoughts, and system logs.")
        
        # CPU/RAM Stats
        if psutil:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            c1, c2 = st.columns(2)
            c1.metric("CPU Usage", f"{cpu}%")
            
            # RAM Color Logic
            ram_delta_color = "normal"
            if ram > 85: ram_delta_color = "inverse"
            c2.metric("RAM Usage", f"{ram}%", delta_color=ram_delta_color)
            if ram > 90:
                st.error("⚠️ High Memory Usage! Performance may degrade.")

        st.divider()
        st.subheader("📜 Live Engine Logs")
        
        # Log Reader
        log_path = os.path.join(project_root, "logs", "engine.log")
        
        col_ctrl, col_view = st.columns([1, 4])
        with col_ctrl:
            auto_refresh = st.toggle("Auto-Refresh", value=True)
            if st.button("🗑️ Clear Logs"):
                open(log_path, 'w').close()
                st.success("Logs cleared.")
                st.rerun()
            
            lines_to_show = st.select_slider("Lines", options=[50, 100, 200, 500, 1000], value=100)
            
        with col_view:
            log_container = st.empty()
            
            # Simple tail implementation
            try:
                if os.path.exists(log_path):
                    with open(log_path, 'r', encoding='utf-8') as f:
                        # Improved: Read last N lines effectively
                         # For small files traverse; for large files seek
                        lines = f.readlines()
                        last_n = lines[-lines_to_show:]
                        log_text = "".join(last_n)
                        
                        st.code(log_text, language="log")
                else:
                    st.info("Log file not found yet (waiting for startup...)")
            except Exception as e:
                st.error(f"Error reading log: {e}")
        
        if auto_refresh:
            time.sleep(2)
            st.rerun()

    elif choice == "Agency Orchestrator":
        render_agency_ui()


    elif choice == "Automation Hub":
        st.header("🤖 Automation Hub")
        st.caption("Autonomous mission control center. Monitor and manage long-running agent loops.")
        
        tab_manager, tab_status = st.tabs(["💬 AI Manager", "📊 Mission Control"])
        
        with tab_manager:
             render_manager_ui()

        with tab_status:
            engine = st.session_state['automation_engine']
            
            # Stats Row
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Status", "Running 🟢" if engine.is_running else "Idle ⚪")
            c2.metric("Missions Run", engine.stats['missions_total'])
            c3.metric("Leads Found", engine.stats['leads_found'])
            c4.metric("Emails Sent", engine.stats['emails_sent'])
            
            st.divider()
            
            col_main, col_logs = st.columns([2, 1])
            
            with col_main:
                st.subheader("Mission Control")
                
                # --- NEW: TABBED VIEW FOR STRATEGY VS TASK ---
                mc_tabs = st.tabs(["🚀 Strategic Missions", "⚡ Task Automation"])
                
                with mc_tabs[0]:
                    st.caption("Execute long-running, multi-agent strategies.")
                    # Pending Strategy Loader
                    if 'pending_strategy' in st.session_state:
                        strat = st.session_state['pending_strategy']
                        st.info(f"Loaded Strategy: **{strat.get('strategy_name', 'Unnamed')}**")
                        
                        if st.button("🚀 Launch Autonomous Mission", type="primary", disabled=engine.is_running):
                            # Start the engine
                            manager = ManagerAgent() # Create a fresh instance
                            engine.start_mission(strat, manager)
                            del st.session_state['pending_strategy'] # Clear pending
                            st.rerun()
                    elif not engine.is_running:
                        st.info("No strategy loaded. Go to Strategy Laboratory to generate one.")

                with mc_tabs[1]:
                    st.caption("Run specific, deterministic standard operating procedures (SOPs).")
                    
                    tasks = list_workflows(type_filter="task")
                    if not tasks:
                        st.info("No 'Task' workflows found. Create one in Workflow Builder with 'type: task'.")
                    else:
                        selected_task = st.selectbox("Select Task / SOP", tasks)
                        if st.button("▶️ Run Task", disabled=engine.is_running):
                            # Adapt the task execution effectively
                            # Ideally we create a temporary strategy wrapper
                            task_data = load_workflow(selected_task)
                            
                            temp_strat = {
                                "strategy_name": f"Task: {selected_task}",
                                "mode": "conductor",
                                "sequence": [{"type": "workflow", "name": selected_task}],
                                "goal": f"Execute task {selected_task}"
                            }
                            
                            manager = ManagerAgent()
                            engine.start_mission(temp_strat, manager)
                            st.rerun()
                
                if engine.is_running:
                    st.markdown(f"**Current Mission:** {engine.current_mission}")
                    if st.button("🛑 STOP AUTOMATION", type="secondary"):
                        engine.stop()
                        st.rerun()
                        
                    st.success("Automation is running in the background. You can navigate away, but do not close the tab.")

            with col_logs:
                st.subheader("Live Logs")
                # Auto-refresh mechanism
                col_ref1, col_ref2 = st.columns([1, 1])
                with col_ref1:
                    if st.button("🔄 Refresh Now"):
                        st.rerun()
                with col_ref2:
                    auto_ref = st.toggle("Auto-Live", value=engine.is_running, key="log_autorefresh")
                
                log_container = st.container(height=400)
                if engine.logs:
                    log_text = "\n".join(engine.logs[::-1]) # Reverse order
                    log_container.code(log_text, language="text")
                else:
                    log_container.write("No logs yet.")
                
                # Trigger rerun if auto-refresh is on and engine is running
                if auto_ref and engine.is_running:
                     time.sleep(2)
                     st.rerun()

    elif choice == "Workflow Builder":
        st.header("🛠️ Workflow Builder")
        st.caption("Design custom agent workflows using markdown.")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.subheader("My Workflows")
            workflows = list_workflows()
            
            # Action: Content Creator
            if st.button("➕ New Workflow", width="stretch"):
                st.session_state['editing_workflow'] = None
                st.session_state['workflow_name'] = ""
                st.session_state['workflow_desc'] = ""
                st.session_state['workflow_content'] = ""
                st.rerun()

            for wf in workflows:
                if st.button(f"📄 {wf}", key=f"sel_{wf}", width="stretch"):
                    data = load_workflow(wf)
                    if data:
                        st.session_state['editing_workflow'] = wf
                        st.session_state['workflow_name'] = wf
                        st.session_state['workflow_desc'] = data['description']
                        st.session_state['workflow_content'] = data['content']
                        st.rerun()
                        
        with col2:
            st.subheader("Editor")
            
            with st.form("workflow_editor_form"):
                w_name = st.text_input("Filename (e.g. my_workflow.md)", value=st.session_state.get('workflow_name', ''))
                w_desc = st.text_input("Description", value=st.session_state.get('workflow_desc', ''))
                w_content = st.text_area("Workflow Steps (Markdown)", value=st.session_state.get('workflow_content', ''), height=400)
                
                c_save, c_del = st.columns([4, 1])
                
                with c_save:
                    if st.form_submit_button("💾 Save Workflow", type="primary", width="stretch"):
                        if w_name and w_content:
                            save_workflow(w_name, w_content, w_desc)
                            st.success(f"Saved {w_name}!")
                            st.session_state['editing_workflow'] = w_name
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Name and Content are required.")
                            
                with c_del:
                    # Fix: Submit button must always be rendered inside form!
                    delete_submitted = st.form_submit_button("🗑️ Delete", type="secondary", width="stretch", disabled=not bool(st.session_state.get('editing_workflow')))
                    
                    if delete_submitted and st.session_state.get('editing_workflow'):
                        delete_workflow(st.session_state['editing_workflow'])
                        st.success("Deleted.")
                        st.session_state['editing_workflow'] = None
                        st.session_state['workflow_name'] = ""
                        st.session_state['workflow_desc'] = ""
                        st.session_state['workflow_content'] = ""
                        time.sleep(1)
                        st.rerun()

    elif choice == "Influencer Scout":
        st.header("🔥 Influencer & Creator Scout")
        st.caption("Find high-impact voices in your niche to promote your product.")
        
        with st.expander("🔍 Discovery Parameters", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                inf_niche = st.text_input("Niche / Topic", placeholder="e.g. Sustainable Fashion, AI Tools")
            with col2:
                inf_platform = st.selectbox("Platform", ["instagram", "tiktok", "twitter", "youtube"])
            with col3:
                inf_limit = st.slider("Results to Scout", 5, 50, 10)
            
            # Follower Filters
            col4, col5 = st.columns(2)
            with col4:
                inf_min_f = st.text_input("Min Followers (e.g. 10k)", placeholder="0")
            with col5:
                inf_max_f = st.text_input("Max Followers", placeholder="No limit")
            
            if st.button("🚀 Scout Influencers", type="primary"):
                agent = InfluencerAgent()
                
                # Parse follower counts
                try:
                    min_followers = agent._parse_follower_count(inf_min_f)
                    max_followers = agent._parse_follower_count(inf_max_f)
                except:
                     min_followers = 0
                     max_followers = 0

                with st.spinner(f"Scouting {inf_platform} for {inf_niche} creators..."):
                    try:
                        results = asyncio.run(agent.scout_influencers(
                            inf_niche, 
                            inf_platform, 
                            inf_limit, 
                            min_followers=min_followers, 
                            max_followers=max_followers
                        ))
                        
                        if not results:
                            st.error("No influencers found. Try a broader niche or different platform.")
                        else:
                            st.session_state['influencer_results'] = results
                            st.success(f"Found {len(results)} potential partners!")
                            time.sleep(1) # Give time to read message
                            st.rerun()
                    except ConnectionError as e:
                        st.error(f"🔌 Search Engine Unavailable: {e}")
                        st.info("💡 Solution: Please open Docker Desktop and wait for the 'searxng' container to start.")

        if 'influencer_results' in st.session_state:
            results = st.session_state['influencer_results']
            
            # Card Grid Layout
            cols = st.columns(3)
            for idx, item in enumerate(results):
                with cols[idx % 3]:
                    with st.container(border=True):
                        st.subheader(item.get('handle', 'Unknown'))
                        st.caption(f"{item.get('platform')} • {item.get('estimated_followers', '?')} followers")
                        st.markdown(f"**Bio Snippet:**_{item.get('bio_snippet', 'No bio found')}_")
                        st.markdown(f"[View Profile]({item.get('url')})")
                        
                        if st.button("Analyze & DM", key=f"inf_dm_{idx}"):
                            # Placeholder for future outreach
                            st.toast("added to outreach queue (Demo)")
    
    elif choice == "Viral Engine":
        st.header("🚀 Viral Engine")
        st.caption("Generate high-velocity content ideas for TikTok, Reels, and Shorts.")
        
        # Initialize Agent
        if 'viral_agent' not in st.session_state:
            st.session_state['viral_agent'] = SocialMediaAgent()
        agent = st.session_state['viral_agent']
        
        col1, col2 = st.columns(2)
        with col1:
            v_niche = st.text_input("Target Niche", placeholder="e.g. AI Productivity Tools", key="ve_niche")
        with col2:
            v_product = st.text_input("Product/Focus", placeholder="e.g. Smarketer Pro", key="ve_prod")
            
        v_platform = st.selectbox("Platform Strategy", ["TikTok Viral", "Instagram Reels", "YouTube Shorts"], key="ve_plat")
        
        if st.button("Generate Viral Concepts", type="primary"):
             if v_niche and v_product:
                 with st.spinner("Analyzing trends and generating hooks..."):
                     context = f"Product: {v_product}, Niche: {v_niche}, Platform: {v_platform}"
                     if v_platform == "TikTok Viral":
                         res = agent.generate_tiktok_strategy(v_niche, v_product)
                     elif v_platform == "Instagram Reels":
                         res = agent.generate_instagram_strategy(v_niche, v_product)
                     else:
                         # Fallback/Custom
                         res = agent.think(f"Generate a viral YouTube Shorts strategy for {v_product} in the {v_niche} niche. Include 3 video concepts with hooks and script outlines.")
                     
                     st.session_state['viral_results'] = res
                     st.session_state['viral_context'] = context
                     st.rerun()
             else:
                 st.warning("Please enter Niche and Product.")
                 
        if 'viral_results' in st.session_state:
            st.divider()
            st.subheader("🔥 Strategy Output")
            st.json(st.session_state['viral_results'])
            
            # Interactive Chat
            render_agent_chat('viral_results', agent, 'viral_context')

        # Save to Library
        if 'viral_results' in st.session_state:
             if st.button("💾 Save Strategy"):
                 save_creative_content(
                     "Social Media", "json", 
                     f"Viral Strategy: {v_product}", 
                     json.dumps(st.session_state['viral_results'])
                 )
                 st.toast("Strategy Saved!")

    
    elif choice == "Tasks":
        st.header("📝 Task Management")
        
        # Load data
        all_tasks = get_tasks()
        pending_tasks = [t for t in all_tasks if t['status'] == 'pending']
        completed_tasks = [t for t in all_tasks if t['status'] == 'completed']
        overdue_tasks = [t for t in pending_tasks if t['due_date'] < time.time()]
        
        # Dashboard Stats
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Total Tasks", len(all_tasks))
        s2.metric("Pending", len(pending_tasks))
        s3.metric("Completed", len(completed_tasks))
        s4.metric("Overdue", len(overdue_tasks), delta_color="inverse")
        
        st.divider()
        
        # Create Task Form
        with st.expander("➕ Create New Task", expanded=len(all_tasks) == 0):
            with st.form("new_task_form"):
                col1, col2 = st.columns(2)
                with col1:
                    description = st.text_input("Task Description", placeholder="e.g. Follow up on proposal")
                    priority = st.selectbox("Priority", ["Low", "Medium", "High", "Urgent"], index=1)
                with col2:
                    task_type = st.selectbox("Type", ["Call", "Email", "Meeting", "Research", "Follow-up", "Task"], index=5)
                    due_date = st.date_input("Due Date")
                
                # Associated Lead
                leads_list = load_data("leads")
                lead_options = {"None": None}
                if not leads_list.empty:
                    for _, row in leads_list.iterrows():
                        label = f"{row['company_name']} ({row['contact_person']})" if row['company_name'] else row['email']
                        lead_options[label] = row['id']
                
                selected_lead_label = st.selectbox("Associate with Lead", list(lead_options.keys()))
                lead_id = lead_options[selected_lead_label]
                
                if st.form_submit_button("Create Task", width="stretch"):
                    if description:
                        # Convert date to timestamp
                        dt = datetime.combine(due_date, datetime.min.time())
                        ts = int(dt.timestamp())
                        create_task(lead_id, description, ts, priority, task_type)
                        st.success("Task created!")
                        st.rerun()
                    else:
                        st.error("Please enter a description.")

        # View Tasks
        tab_active, tab_completed = st.tabs(["📋 Active Tasks", "✅ Completed"])
        
        with tab_active:
            if not pending_tasks:
                st.info("No active tasks. Time to relax!")
            else:
                # Group by priority for better view? Or just list with badges
                for t in pending_tasks:
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([0.1, 3, 1])
                        
                        # Priority indicator
                        p_color = {"Low": "gray", "Medium": "blue", "High": "orange", "Urgent": "red"}.get(t['priority'], "blue")
                        
                        with c2:
                            st.markdown(f"**{t['description']}**")
                            lead_name = t.get('company_name') or "General Task"
                            st.caption(f"📌 {t['task_type']} | 🏢 {lead_name} | 📅 Due: {pd.to_datetime(t['due_date'], unit='s').strftime('%Y-%m-%d')}")
                        
                        with c3:
                            st.markdown(f":{p_color}[{t['priority']}]")
                            col_b1, col_b2 = st.columns(2)
                            if col_b1.button("Done", key=f"done_{t['id']}"):
                                mark_task_completed(t['id']); st.rerun()
                            if col_b2.button("🗑️", key=f"del_{t['id']}"):
                                delete_task(t['id']); st.rerun()

        with tab_completed:
            if not completed_tasks:
                st.write("No completed tasks yet.")
            else:
                for t in completed_tasks:
                    with st.container():
                        c1, c2 = st.columns([4, 1])
                        with c1:
                            st.markdown(f"~~{t['description']}~~")
                            st.caption(f"Done on {pd.to_datetime(t['created_at'], unit='s').strftime('%Y-%m-%d')}") # Using created_at since finished_at isn't in schema yet
                        with c2:
                            if st.button("Delete", key=f"del_c_{t['id']}"):
                                delete_task(t['id']); st.rerun()

        # 3. Page Level Chat
        render_page_chat(
            "Task Management", 
            ManagerAgent(), 
            json.dumps(all_tasks, indent=2)
        )

    elif choice == "Social Scheduler":
        render_social_scheduler_page()

    elif choice == "Social Pulse":
        render_social_pulse_page()

    elif choice == "SEO Audit":
        st.header("📈 SEO Site Audit")
        url_to_audit = st.text_input("Website URL", placeholder="https://example.com")
        if st.button("Run Audit"):
            agent = SEOExpertAgent()
            with st.spinner("Analyzing site..."):
                report = asyncio.run(agent.audit_site(url_to_audit))
                st.session_state['last_seo_report'] = report
                st.rerun()

        if 'last_seo_report' in st.session_state:
            report = st.session_state['last_seo_report']
            st.json(report)
            
            if st.button("📝 Generate & Publish SEO Blog Post"):
                agent = SEOExpertAgent()
                with st.spinner("Drafting content and publishing..."):
                    # Basic logic: Generate a title and content from the audit report
                    title = f"SEO Analysis for {url_to_audit}"
                    content = f"Site Audit Report:\n{json.dumps(report, indent=2)}"
                    
                    res = agent.publish_to_wordpress(title, content)
                    if res["status"] == "success":
                        st.success("Successfully published to WordPress!")
                    else:
                        st.error(f"Publishing failed: {res.get('error')}")

    elif choice == "Keyword Research":
        st.header("🔑 Keyword Strategy")
        topic = st.text_input("Niche / Topic", placeholder="commercial plumbing repairs")
        if st.button("Research Keywords"):
            agent = SEOExpertAgent()
            with st.spinner("Finding high-intent keywords..."):
                report = agent.research_keywords(topic)
                st.json(report)

    elif choice == "Link Wheel Builder":
        st.header("🎡 Link Wheel Architect")
        st.caption("Design authority-funneling structures (SEnuke Style).")
        
        m_site = st.text_input("Money Site URL", placeholder="https://your-main-site.com")
        lw_niche = st.text_input("Niche", placeholder="Roofing")
        lw_strategy = st.selectbox("Strategy", ["Standard Wheel", "Double Link Wheel", "The Authority Funnel"])
        
        if st.button("Design Structure"):
            agent = SEOExpertAgent()
            with st.spinner("Calculating PageRank flow and tier structures..."):
                plan = agent.design_link_wheel(m_site, lw_niche, strategy=lw_strategy)
                st.session_state['last_lw_plan'] = plan
                st.rerun()

        if 'last_lw_plan' in st.session_state:
            plan = st.session_state['last_lw_plan']
            st.subheader(f"Strategy: {plan.get('strategy_name')}")
            
            # Render Mermaid from Agent Output
            st.info("Visualizing Link Graph...")
            mermaid_code = plan.get('diagram_instructions', "")
            if "graph " in mermaid_code:
                st.markdown(f"```mermaid\n{mermaid_code}\n```")
            else:
                # Fallback to a dynamic structure based on the plan
                st.markdown(f"```mermaid\ngraph TD\nMS[{m_site}]\n" + \
                    "\n".join([f"T1_{i}[Tier 1 Property] --> MS" for i in range(3)]) + \
                    "\n```")
            
            st.json(plan)
            
            if st.button("💾 Save Plan to Library"):
                save_creative_content(
                    "SEO Expert", "json", 
                    f"Link Wheel Plan: {plan.get('strategy_name')}", 
                    json.dumps(plan)
                )
                st.toast("Plan saved to library!")
            
            st.divider()
            col_lw1, col_lw2 = st.columns([1, 1])
            with col_lw1:
                if st.button("🚀 Execute Autonomous Mission", type="primary"):
                    with st.status("SEO Expert is executing Link Wheel mission...") as status:
                        agent = SEOExpertAgent()
                        results = asyncio.run(agent.run_link_wheel_mission(
                            m_site, 
                            lw_niche, 
                            strategy=lw_strategy,
                            status_callback=lambda m: status.write(m)
                        ))
                        st.session_state['last_lw_results'] = results
                        status.update(label="Link Wheel Execution & Indexation Boost Complete!", state="complete")
            
            if 'last_lw_results' in st.session_state:
                st.success("Mission Complete! Check the execution logs above.")
                with st.expander("View Execution Details"):
                    results = st.session_state['last_lw_results']
                    st.json(results)
                    
                    if 'indexing_boost' in results:
                        st.subheader("📡 Indexing Status")
                        ib = results['indexing_boost']
                        c_rss, c_bm = st.columns(2)
                        with c_rss:
                            st.write(f"✅ RSS Feeds: {len(ib.get('rss', {}).get('distribution_results', []))} Pings sent.")
                        with c_bm:
                            st.write(f"✅ Bookmarks: {len(ib.get('bookmarks', {}))} URLs processed.")

                    if st.button("💾 Save Results to Library"):
                        save_creative_content(
                            "SEO Expert", "json", 
                            f"Link Wheel Results: {plan.get('strategy_name', 'Unnamed')}", 
                            json.dumps(st.session_state['last_lw_results'])
                        )
                        st.toast("Results saved to library!")

    elif choice == "Mass Tools":
        render_mass_tools_page()

    elif choice == "Lead Discovery":
        st.subheader("🔍 Find New Leads")
        with st.form("search_form"):
            query = st.text_input("Search Query", "marketing agencies in Austin")
            col_search_1, col_search_2 = st.columns(2)
            with col_search_1:
                niche = st.text_input("Target Niche Filter (Optional)", "Marketing")
            with col_search_2:
                # Default to config value, but allow override
                search_conf = config.get("search") or {}
                default_max = search_conf.get("max_results", 50)
                limit = st.number_input("Max Results", min_value=1, max_value=10000, value=default_max, help="Limit the number of leads to fetch.")
            
            # Load available profiles from config
            search_config = config.get("search") or {}
            available_profiles = list(search_config.get("profiles", {}).keys())
            if not available_profiles:
                available_profiles = ["default"]
                
            selected_profiles = st.multiselect("Search Profiles", available_profiles, default=["default"])
            
            with st.expander("🚫 Domain Filters (Exclusions)"):
                st.caption("URLs containing these patterns will be ignored.")
                # Load defaults
                default_exclusions = search_conf.get("exclude_patterns", [])
                
                # CSV Upload
                exclusion_csv = st.file_uploader("Upload CSV Exclusion List", type=["csv"], help="One domain/pattern per line")
                if exclusion_csv:
                     try:
                         df_uploaded = pd.read_csv(exclusion_csv)
                         # Assume first column is what we want if no standard name
                         col_name = df_uploaded.columns[0]
                         new_patterns = df_uploaded[col_name].astype(str).tolist()
                         # Merge unique
                         default_exclusions = list(set(default_exclusions + new_patterns))
                         st.success(f"Added {len(new_patterns)} patterns from CSV.")
                     except Exception as e:
                         st.error(f"Error reading CSV: {e}")

                # Convert to df for editor with explicit types to avoid StreamlitAPIException
                df_exclude = pd.DataFrame({
                    'Active': [True] * len(default_exclusions),
                    'Pattern': default_exclusions
                }).astype({'Active': bool, 'Pattern': str})
                
                edited_exclusions = st.data_editor(
                    df_exclude, 
                    num_rows="dynamic", 
                    key="exclusion_editor",
                    column_config={
                        "Active": st.column_config.CheckboxColumn(required=True, default=True),
                        "Pattern": st.column_config.TextColumn(required=True)
                    }
                )
                
                # Filter only Active patterns
                if not edited_exclusions.empty:
                    current_exclusions = edited_exclusions[edited_exclusions["Active"] == True]["Pattern"].tolist()
                else:
                    current_exclusions = []

            with st.expander("🛡️ Quality Gate (ICP Criteria)"):
                st.caption("AI will filter out leads that do not match these criteria.")
                enable_gate = st.toggle("Enable Quality Gate", value=True)
                
                # Safe config access
                qg_config = config.get("quality_gate") or {}
                
                col_icp1, col_icp2 = st.columns(2)
                with col_icp1:
                    default_must = "\n".join(qg_config.get("must_haves", []))
                    must_have = st.text_area("Must Haves", 
                        value=default_must,
                        placeholder="e.g. B2B Software, Uses Shopify, Based in USA",
                        help="Leads MUST match these to pass.")
                with col_icp2:
                    default_breakers = "\n".join(qg_config.get("deal_breakers", []))
                    deal_breakers = st.text_area("Deal Breakers", 
                        value=default_breakers,
                        placeholder="e.g. Agencies, Non-profits, Students",
                        help="Leads matching these will be rejected (0 score).")
                
                icp_criteria = None
                if enable_gate and (must_have.strip() or deal_breakers.strip()):
                    icp_criteria = f"Must Haves:\n{must_have}\n\nDeal Breakers:\n{deal_breakers}"

            with st.expander("🚀 Deep Intelligence (Enrichment)"):
                st.caption("Automatically find social profiles and hiring intent signals.")
                auto_enrich = st.checkbox("Auto-Enrich Leads (LinkedIn, Twitter, Intent)", value=False)


            st.warning("⚠️ Do not leave this page while the search is running. It will stop the process.")
            
            st.divider()
            submitted = st.form_submit_button("Start Search 🚀", type="primary", width="stretch")
            
            if submitted:
                # Check for empty Quality Gate
                if enable_gate and not icp_criteria:
                     st.warning("⚠️ Quality Gate enabled but criteria fields are empty. Proceeding without filtering (All leads will pass).")

                st.info("Agent is running... (See logs below)")

                # Log Container
                if not selected_profiles:
                    selected_profiles = ["default"]

                # Modern Status UI
                with st.status("🕵️‍♂️ Agent is scouting the web...", expanded=True) as status:
                    def update_log(msg):
                        status.write(msg)
                        if "Found:" in msg:
                            st.toast(msg, icon="🎉")
                    
                    # Async wrapper - CAPTURE RESULTS
                    results = asyncio.run(run_outreach(
                        query, 
                        profile_names=selected_profiles, 
                        target_niche=niche, 
                        status_callback=update_log,
                        exclusions=current_exclusions,
                        icp_criteria=icp_criteria,
                        max_results=limit,
                        auto_enrich=auto_enrich
                    ))
                    
                    status.update(label=f"Search Mission Complete! {len(results) if results else 0} Leads Found.", state="complete", expanded=False)
                
                if results:
                    st.session_state['last_search_results'] = results
                    st.success(f"Successfully found and saved {len(results)} new leads!")
                else:
                    st.warning("Search complete, but no new unique leads were found.")
            
        # --- RESULTS DISPLAY AREA (Outside the form) ---
        if st.session_state.get('last_search_results'):
            st.divider()
            st.subheader("📋 Latest Search Results")

            results_data = st.session_state['last_search_results']
            
            # Flatten for display
            display_list = []
            for r in results_data:
                display_list.append({
                    "Company": r.get('details', {}).get('business_name') or r.get('url'),
                    "Emails": ", ".join(r.get('emails', [])),
                    "Industry": r.get('details', {}).get('industry') or niche,
                    "Score": r.get('analysis', {}).get('score', 0),
                    "URL": r.get('url'),
                    "ID": r.get('id')
                })
            
            df_res = pd.DataFrame(display_list)
            
            # 1. Standard Data Management Bar
            def clear_results():
                st.session_state['last_search_results'] = None
                st.rerun()

            render_data_management_bar(
                display_list, 
                filename_prefix="leads_discovery", 
                on_delete=clear_results
            )

            # 2. Enhanced Table
            edited_df = render_enhanced_table(df_res, key="lead_discovery_table")
            
            # --- NEW: Lead Drill-Down Panel ---
            selected_indices = edited_df[edited_df['Select'] == True].index.tolist()
            if selected_indices:
                st.divider()
                st.subheader("🔎 Lead Inspector")
                
                # If multiple selected, showing the first one as "Deep Dive Focus"
                # but bulk actions still apply to all.
                focus_idx = selected_indices[0]
                focus_lead = results_data[focus_idx]
                
                with st.container(border=True):
                    d_col1, d_col2 = st.columns([2, 1])
                    with d_col1:
                        st.markdown(f"### {focus_lead.get('details', {}).get('business_name') or focus_lead.get('url')}")
                        st.caption(f"🌐 {focus_lead.get('url')}")
                        
                        st.markdown("#### 📧 Contact Info")
                        emails = focus_lead.get('emails', [])
                        if emails:
                            for e in emails:
                                st.code(e, language="text")
                        else:
                            st.warning("No emails found yet.")
                        
                        st.markdown("#### 🧠 AI Analysis")
                        st.write(focus_lead.get('analysis', {}).get('reasoning', 'No deep analysis available.'))
                        
                    with d_col2:
                        st.metric("Match Score", f"{focus_lead.get('analysis', {}).get('score', 0)}/100")
                        
                        st.markdown("#### Socials")
                        socials = focus_lead.get('social_links', {})
                        if socials:
                            for plat, link in socials.items():
                                st.markdown(f"[{plat.capitalize()}]({link})")
                        else:
                            st.caption("No socials found.")
                            
                        st.divider()
                        if st.button("✨ Enrich This Lead", key=f"enrich_{focus_lead.get('id')}"):
                            with st.spinner("Enriching..."):
                                # Dummy placeholder for enrichment hook
                                time.sleep(1) 
                                st.toast("Enrichment Request Queued (Demo)")
            
            # --- NEW: Bulk Action: Add to Campaign ---
            st.divider()
            st.subheader("⚡ Bulk Actions")
            col_bulk1, col_bulk2 = st.columns([2, 1])
            
            with col_bulk1:
                campaigns = get_all_campaigns()
                if campaigns:
                    camp_options = {c['name']: c['id'] for c in campaigns}
                    target_camp = st.selectbox("Select Target Campaign", list(camp_options.keys()))
                else:
                    st.warning("No active campaigns found. Create one first.")
                    target_camp = None
            
            with col_bulk2:
                selected_leads = edited_df[edited_df['Select'] == True]
                if st.button(f"📥 Add {len(selected_leads)} to Campaign", type="primary", disabled=not target_camp or selected_leads.empty):
                    camp_id = camp_options[target_camp]
                    added_count = 0
                    for _, row in selected_leads.iterrows():
                        if add_lead_to_campaign(camp_id, row['ID']):
                            added_count += 1
                    st.success(f"Successfully added {added_count} leads to '{target_camp}'!")
                    time.sleep(1)
            
            st.divider()
            
            # 3. Page Level Chat
            render_page_chat(
                "Lead Results", 
                ResearcherAgent(), 
                json.dumps(display_list, indent=2)
            )

            st.info("💡 These leads are now saved in your CRM. You can find them in the 'CRM Dashboard'.")

    elif choice == "Campaigns":
        render_campaign_page()

    elif choice == "Product Lab":
        render_pm_ui()

    elif choice == "Strategy Laboratory":
        st.header("🔬 Strategy Laboratory")
        st.caption("Conceptualize complex campaigns and manage collective agent intelligence.")
        
        lab_tabs = st.tabs(["🔗 Multichannel sequence", "🧠 Memory Browser"])
        
        with lab_tabs[0]:
            st.subheader("Multichannel Sequence Planner")
            st.write("The Manager Agent will plan a multi-touch sequence across Email and LinkedIn.")
            m_goal = st.text_input("Campaign Goal", placeholder="e.g. 'Find 5 SEO agencies and draft multi-touch outreach'")
            
            if st.button("Plan & Draft Mission"):
                if m_goal:
                    with st.status("Manager orchestrating mission...", expanded=True) as status:
                        agent = ManagerAgent()
                        report = asyncio.run(agent.run_mission(m_goal))
                        st.session_state['last_mission_report'] = report
                        st.session_state['mission_context'] = m_goal
                        status.update(label="Mission Planned!", state="complete")
            
            if 'last_mission_report' in st.session_state:
                report = st.session_state['last_mission_report']
                st.divider()
                st.markdown(f"### 📋 Mission Report: {report['plan'].get('strategy_name', 'Custom Mission')}")
                st.write(f"**ICP:** {report['plan'].get('icp_criteria')}")
                
                for idx, lead in enumerate(report.get('leads', [])):
                    with st.expander(f"👤 Lead: {lead['url']}"):
                        st.write("**Drafts:**")
                        if 'email' in lead['drafts']:
                            st.markdown("--- Email ---")
                            st.json(lead['drafts']['email'])
                        if 'linkedin' in lead['drafts']:
                            st.markdown("--- LinkedIn ---")
                            st.json(lead['drafts']['linkedin'])

        with lab_tabs[1]:
            st.subheader("🧠 Memory Browser")
            st.write("Browse recorded agent thoughts and decision paths.")
            
            # Fetch memory
            from memory import memory_store
            memory_data = memory_store.get_all_memory() # Returns dict {agent_role: {key: {content, timestamp, metadata}}}
            
            if not memory_data:
                st.info("Neural network is fresh. No memories recorded yet.")
            else:
                roles = ["All Agents"] + sorted(list(memory_data.keys()))
                sel_role = st.selectbox("🤖 Filter Agent memories", roles)
                
                search_q = st.text_input("🔍 Search memories", placeholder="Keyword...")
                
                if search_q:
                    # Logic for search (simplified/placeholder if not fully implemented in memory_store)
                    st.info(f"Searching for '{search_q}' in {sel_role} memories...")
                else:
                    # Grouped Index
                    if sel_role == "All Agents":
                        for role, entries in memory_data.items():
                            with st.expander(f"🤖 {role} ({len(entries)} entries)"):
                                for key, data in entries.items():
                                    st.markdown(f"**{key}:** {data['content']}")
                                    st.divider()
                    else:
                        entries = memory_data.get(sel_role, {})
                        st.write(f"Showing memories for: **{sel_role}**")
                        for key, data in entries.items():
                            with st.expander(f"🔑 {key}"):
                                st.write(data['content'])
                                st.caption(f"Recorded: {data['timestamp']}")

    elif choice == "Agent Lab":
        render_agent_lab()



    elif choice == "Creative Library":
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
            
            selected_items = edited_lib[edited_lib['Select'] == True]
            if not selected_items.empty:
                if st.button(f"🗑️ Delete {len(selected_items)} Selected Items", type="secondary"):
                    for item_id in selected_items['id'].tolist():
                        delete_creative_item(item_id)
                    st.success("Deleted!")
                    st.rerun()

            st.divider()
            st.subheader("🖼️ Gallery View")
            for item in display_items:
                with st.expander(f"📌 {item['agent_type']}: {item['title']} ({time.strftime('%Y-%m-%d', time.localtime(item['created_at']))})", expanded=False):
                    if item['content_type'] == 'image':
                        # ... (keep existing image display logic)
                        st.image(item['body'])
                        st.caption(f"Prompt: {item['title']}")
                        st.markdown(f"[Download Image](file://{item['body']})")
                    else:
                        try:
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

    elif choice == "Affiliate Command":
        render_affiliate_ui()

    elif choice == "Settings":
        render_settings_page()

    elif choice == "Agent Lab":
        render_agent_lab()
        
    elif choice == "Agent Factory":
        st.header("🏭 Agent Factory")
        st.caption("Create and manage custom AI agents for specific tasks.")
        
        tab_list, tab_create, tab_run = st.tabs(["📂 My Agents", "➕ Create Agent", "🤖 Run Agent"])
        
        with tab_create:
            st.subheader("Define New Agent")
            with st.form("create_agent_form"):
                ca_name = st.text_input("Agent Name", placeholder="e.g. Poet, Code Reviewer")
                ca_role = st.text_input("Role", placeholder="e.g. Senior Poet, Python Expert")
                ca_goal = st.text_area("Goal", placeholder="e.g. Write beautiful haikus about specific topics.")
                ca_sys = st.text_area("System Prompt (Optional)", placeholder="Base instructions/personality...", height=150)
                
                if st.form_submit_button("Create Agent", type="primary"):
                    if ca_name and ca_role and ca_goal:
                        create_custom_agent(ca_name, ca_role, ca_goal, ca_sys)
                        st.success(f"Agent '{ca_name}' created successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Name, Role, and Goal are required.")
 
        with tab_list:
            st.subheader("Installed Agents")
            agents = get_custom_agents()
            if not agents:
                st.info("No custom agents found. Create one in the next tab!")
            else:
                for ag in agents:
                    with st.container(border=True):
                        c1, c2, c3 = st.columns([1, 3, 1])
                        with c1:
                            st.subheader(f"🤖 {ag['name']}")
                        with c2:
                            st.write(f"**Role:** {ag['role']}")
                            st.write(f"**Goal:** {ag['goal']}")
                        with c3:
                            if st.button("Delete", key=f"del_ag_{ag['id']}"):
                                delete_custom_agent(ag['id'])
                                st.rerun()

        with tab_run:
            st.subheader("Run Custom Agent")
            agents = get_custom_agents()
            if not agents:
                st.warning("Create an agent first!")
            else:
                selected_agent_name = st.selectbox("Select Agent", [a['name'] for a in agents])
                # Get full agent details
                selected_agent_data = next(a for a in agents if a['name'] == selected_agent_name)
                
                # Instantiate Agent
                custom_agent = CustomAgent(
                    name=selected_agent_data['name'],
                    role=selected_agent_data['role'],
                    goal=selected_agent_data['goal'],
                    system_prompt=selected_agent_data['system_prompt']
                )
                
                # Context Input
                context_input = st.text_area("Context / Input", height=150, key="ca_context", placeholder="Enter the text or data the agent should process...")
                
                # Proxy Toggle
                use_proxies = st.checkbox("Use Elite Proxy Pool", value=True, help="Enable if this agent performs web tasks or needs higher anonymity.")
                custom_agent.proxy_enabled = use_proxies

                if st.button("Run Agent", type="primary"):
                    if context_input:
                        with st.spinner(f"{selected_agent_name} is thinking..."):
                            response = custom_agent.think(context_input)
                            st.session_state['last_custom_agent_response'] = response
                            st.rerun()
                    else:
                        st.error("Please provide some input.")
                
                # Show Result & Tuning
                if 'last_custom_agent_response' in st.session_state:
                    st.divider()
                    st.subheader("Result")
                    st.write(st.session_state['last_custom_agent_response'])
                    
                    # Agent Lab Tuning Integration
                    render_agent_chat("last_custom_agent_response", custom_agent, "ca_context")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        # Allow Streamlit Control Flow Exceptions to pass through
        if type(e).__name__ in ["RerunException", "StopException"]:
            raise e
            
        import traceback
        error_msg = f"CRITICAL: App crashed: {e}\n{traceback.format_exc()}"
        print(error_msg, file=sys.stderr)
        try:
            with open("logs/crash.log", "a") as f:
                f.write(f"\n[{datetime.now()}] {error_msg}\n")
        except:
            pass
    except BaseException as e:
        # Allow Streamlit Control Flow Exceptions to pass through (RerunException is usually BaseException)
        if type(e).__name__ in ["RerunException", "StopException"]:
            raise e

        import traceback
        # Catch SystemExit and others
        error_msg = f"CRITICAL: App crashed with BaseException: {e}\n{traceback.format_exc()}"
        print(error_msg, file=sys.stderr)
        try:
            with open("logs/crash.log", "a") as f:
                f.write(f"\n[{datetime.now()}] {error_msg}\n")
        except:
            pass
