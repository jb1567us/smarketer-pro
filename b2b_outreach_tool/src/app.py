import streamlit as st
import pandas as pd
import sqlite3
import os
import sys
import asyncio
import time
import subprocess
import platform
from dotenv import load_dotenv

load_dotenv()

# Ensure src is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_connection, get_pain_points, save_template, get_templates, init_db, clear_all_leads, delete_leads, get_campaign_analytics, get_daily_engagement
from workflow import run_outreach
from campaign_manager import start_campaign_step_research, start_campaign_step_copy, start_campaign_step_send, refine_campaign_step_research
from mailer import Mailer
from config import config, reload_config
from agents import ResearcherAgent, QualifierAgent, CopywriterAgent, ReviewerAgent, SyntaxAgent, UXAgent, ManagerAgent, GraphicsDesignerAgent

st.set_page_config(page_title="B2B Outreach Agent", layout="wide", page_icon="🚀")

# Import UI Styles
from ui.styles import load_css
load_css()


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

def load_data(table):
    conn = get_connection()
    df = pd.read_sql_query(f"SELECT * from {table}", conn)
    conn.close()
    return df

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

def main():
    st.title("🚀 B2B Outreach Agent")

    menu = ["Dashboard", "Lead Discovery", "Campaign Manager", "Agent Lab", "Analytics", "Settings"]
    menu = ["Dashboard", "Lead Discovery", "Campaign Manager", "Agent Lab", "Analytics", "Settings"]
    choice = st.sidebar.selectbox("Navigation", menu)

    with st.sidebar:
        st.divider()
        if st.button("🛑 Terminate Session"):
            with st.spinner("Saving state and shutting down..."):
                terminate_session()

    if choice == "Analytics":
        st.header("📊 Campaign Analytics")
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

    if choice == "Dashboard":
        st.subheader("Overview")
        try:
            leads = load_data("leads")
            
            # Filter by Source/Campaign
            if 'source' in leads.columns and not leads.empty:
                sources = ["All"] + sorted(list(leads['source'].astype(str).unique()))
                selected_source = st.selectbox("📂 Filter by Campaign:", sources)
                
                if selected_source != "All":
                    leads = leads[leads['source'] == selected_source]
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Leads", len(leads))
            col2.metric("Nurtured", len(leads[leads['status'] == 'nurtured']))
            col3.metric("Pending", len(leads[leads['status'] == 'new']))
            
            # Add selection column for deletion
            select_all = st.checkbox("Select All")
            leads['Select'] = True if select_all else False
            # Reorder to put Select first
            cols = ['Select'] + [c for c in leads.columns if c != 'Select']
            leads = leads[cols]

            edited_df = st.data_editor(
                leads,
                hide_index=True,
                column_config={"Select": st.column_config.CheckboxColumn(required=True)},
                disabled=[c for c in leads.columns if c != "Select"]
            )
            
            # Check for selected rows
            selected_rows = edited_df[edited_df['Select'] == True]
            
            if not selected_rows.empty:
                if st.button(f"🗑️ Delete Selected ({len(selected_rows)})"):
                    delete_ids = selected_rows['id'].tolist()
                    delete_leads(delete_ids)
                    st.success(f"Deleted {len(delete_ids)} leads.")
                    time.sleep(1)
                    st.rerun()
            
            with st.expander("🛠️ Data Management"):
                st.write("Manage your leads database.")
                
                m_col1, m_col2 = st.columns(2)
                
                with m_col1:
                    if st.button("🗑️ Clear Database (Delete All)"):
                        clear_all_leads()
                        st.warning("Database cleared.")
                        time.sleep(1)
                        st.rerun()

                st.divider()
                st.markdown("#### 📤 Import / Export")
                
                ie_col1, ie_col2 = st.columns(2)
                
                with ie_col1:
                    # Export CSV
                    csv = leads.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download CSV (Export)",
                        data=csv,
                        file_name='leads_export.csv',
                        mime='text/csv',
                    )

                with ie_col2:
                    # Import CSV
                    uploaded_file = st.file_uploader("Upload CSV (Import)", type=['csv'], help="Required columns: Email, URL")
                    if uploaded_file is not None:
                        if st.button("Start Import"):
                             process_csv_upload(uploaded_file, default_source="import", default_category="imported")
                
                st.divider()
                st.caption("To delete specific leads, use the checkbox grid above.")

        except Exception as e:
            st.error(f"Error loading dashboard: {e}")
            if st.button("Initialize Database"):
                init_db()
                st.success("Database initialized.")

    elif choice == "Lead Discovery":
        st.subheader("🔍 Find New Leads")
        with st.form("search_form"):
            query = st.text_input("Search Query", "marketing agencies in Austin")
            col_search_1, col_search_2 = st.columns(2)
            with col_search_1:
                niche = st.text_input("Target Niche Filter (Optional)", "Marketing")
            with col_search_2:
                # Default to config value, but allow override
                default_max = config.get("search", {}).get("max_results", 50)
                limit = st.number_input("Max Results", min_value=1, max_value=10000, value=default_max, help="Limit the number of leads to fetch.")
            
            # Load available profiles from config
            available_profiles = list(config["search"].get("profiles", {}).keys())
            if not available_profiles:
                available_profiles = ["default"]
                
            selected_profiles = st.multiselect("Search Profiles", available_profiles, default=["default"])
            
            with st.expander("🚫 Domain Filters (Exclusions)"):
                st.caption("URLs containing these patterns will be ignored.")
                # Load defaults
                default_exclusions = config.get("search", {}).get("exclude_patterns", [])
                
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

                # Convert to df for editor
                import pandas as pd
                # Create DataFrame with Active column defaulting to True
                df_exclude = pd.DataFrame({
                    'Active': [True] * len(default_exclusions),
                    'Pattern': default_exclusions
                })
                
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
                
                col_icp1, col_icp2 = st.columns(2)
                with col_icp1:
                    default_must = "\n".join(config.get("quality_gate", {}).get("must_haves", []))
                    must_have = st.text_area("Must Haves", 
                        value=default_must,
                        placeholder="e.g. B2B Software, Uses Shopify, Based in USA",
                        help="Leads MUST match these to pass.")
                with col_icp2:
                    default_breakers = "\n".join(config.get("quality_gate", {}).get("deal_breakers", []))
                    deal_breakers = st.text_area("Deal Breakers", 
                        value=default_breakers,
                        placeholder="e.g. Agencies, Non-profits, Students",
                        help="Leads matching these will be rejected (0 score).")
                
                icp_criteria = None
                if enable_gate and (must_have.strip() or deal_breakers.strip()):
                    icp_criteria = f"Must Haves:\n{must_have}\n\nDeal Breakers:\n{deal_breakers}"

            st.warning("⚠️ Do not leave this page while the search is running. It will stop the process.")
            submitted = st.form_submit_button("Start Search")
            
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
                    
                    # Async wrapper
                    asyncio.run(run_outreach(
                        query, 
                        profile_names=selected_profiles, 
                        target_niche=niche, 
                        status_callback=update_log,
                        exclusions=current_exclusions,
                        icp_criteria=icp_criteria,
                        max_results=limit
                    ))
                    
                    status.update(label="Search Mission Complete!", state="complete", expanded=False)
                
                st.success("Search complete!")
                time.sleep(2)
                st.rerun()

    elif choice == "Campaign Manager":
        from ui.components import render_step_progress, premium_header
        
        premium_header("Smart Nurture Campaigns", "Create personalised email sequences using AI research.")

        # Stepper State Management
        if 'campaign_step' not in st.session_state:
            st.session_state['campaign_step'] = 0
            
        steps = ["Setup", "Research", "Strategy", "Content", "Launch"]
        render_step_progress(steps, st.session_state['campaign_step'])
        
        current_step = st.session_state['campaign_step']
        
        # --- STEP 1: SETUP ---
        if current_step == 0:
            with st.container():
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.markdown("### 🎯 Campaign Goal")
                    niche_input = st.text_input("Target Niche", value=st.session_state.get('niche_input', "Interior Design"))
                    product_name = st.text_input("Product Name", value=st.session_state.get('product_name', ""))
                
                with col2:
                    st.markdown("### 📝 Context")
                    product_context = st.text_area("Product & Service Details", 
                        value=st.session_state.get('product_context', ""),
                        height=150,
                        help="Describe your offering so the AI can map pain points to your solution.")
                
                st.session_state['niche_input'] = niche_input
                st.session_state['product_name'] = product_name
                st.session_state['product_context'] = product_context
                
                if st.button("Next: Research Pain Points ➡", type="primary"):
                    if niche_input and product_context:
                         st.session_state['campaign_step'] = 1
                         st.rerun()
                    else:
                        st.warning("Please fill in Niche and Context to proceed.")

        # --- STEP 2: RESEARCH ---
        elif current_step == 1:
            st.markdown("### 🧠 AI Analysis")
            st.info(f"Analyzing pain points for: **{st.session_state['niche_input']}**")
            
            if 'pain_points' not in st.session_state:
                with st.spinner("Deep Research Agent is analyzing market data..."):
                    # Call backend
                    points = start_campaign_step_research(
                        st.session_state['niche_input'], 
                        st.session_state['product_context']
                    )
                    st.session_state['pain_points'] = points
                    st.rerun()
            
            else:
                # Display Results
                for p in st.session_state['pain_points']:
                    with st.expander(f"📍 {p['title']}", expanded=True):
                        st.write(p['description'])
                
                col_back, col_next = st.columns([1, 5])
                with col_back:
                    if st.button("⬅ Back"):
                        st.session_state['campaign_step'] = 0
                        st.rerun()
                with col_next:
                    if st.button("Next: Select Strategy ➡", type="primary"):
                        st.session_state['campaign_step'] = 2
                        st.rerun()
                    if st.button("🔄 Regenerate Research"):
                        del st.session_state['pain_points']
                        st.rerun()

        # --- STEP 3: STRATEGY ---
        elif current_step == 2:
            st.markdown("### 🏹 Select Attack Vector")
            st.write("Choose the most compelling angle for your campaign.")
            
            selected_pain = st.radio(
                "Select Focus:", 
                [p['title'] for p in st.session_state['pain_points']],
                index=0
            )
            
            st.markdown("#### Tuning Instructions (Optional)")
            refine_feedback = st.text_input("e.g., 'Make it friendlier' or 'Focus on ROI'")

            col_back, col_next = st.columns([1, 5])
            with col_back:
                if st.button("⬅ Back"):
                    st.session_state['campaign_step'] = 1
                    st.rerun()
            with col_next:
                if st.button("Generate Email Sequence ➡", type="primary"):
                    st.session_state['selected_pain'] = selected_pain
                    st.session_state['refine_feedback'] = refine_feedback
                    st.session_state['campaign_step'] = 3
                    st.rerun()

        # --- STEP 4: CONTENT ---
        elif current_step == 3:
            st.markdown("### ✍️ Content Generation")
            
            if 'sequence' not in st.session_state:
                with st.spinner("Copywriter Agent is drafting emails..."):
                    pain_obj = next(p for p in st.session_state['pain_points'] if p['title'] == st.session_state['selected_pain'])
                    seq = start_campaign_step_copy(
                        st.session_state['niche_input'], 
                        pain_obj, 
                        st.session_state['product_name'], 
                        st.session_state['product_context']
                    )
                    st.session_state['sequence'] = seq
                    st.rerun()
            else:
                for email in st.session_state['sequence']:
                    with st.expander(f"📧 {email['stage'].upper()}: {email['subject']}", expanded=False):
                        st.markdown(email['body'], unsafe_allow_html=True)
                
                col_back, col_next = st.columns([1, 5])
                with col_back:
                    if st.button("⬅ Back"):
                        st.session_state['campaign_step'] = 2
                        del st.session_state['sequence'] # Reset if going back to regen
                        st.rerun()
                with col_next:
                     if st.button("Approved! Go to Launch ➡", type="primary"):
                         st.session_state['campaign_step'] = 4
                         st.rerun()
                     if st.button("🔄 Regenerate Copy"):
                         del st.session_state['sequence']
                         st.rerun()

        # --- STEP 5: LAUNCH ---
        elif current_step == 4:
            st.markdown("### 🚀 Launch Control")

            with st.expander("📤 Import Leads for this Campaign"):
                 st.info("Upload a CSV to add leads specifically to this campaign flow.")
                 camp_upload = st.file_uploader("Upload CSV (Single Column Email or Standard Format)", type=['csv'], key="camp_csv")
                 if camp_upload and st.button("Import to Campaign"):
                      # Use campaign_manager source so we can track, and status=new is default
                      process_csv_upload(camp_upload, default_source="campaign_manager", default_category=f"campaign_{int(time.time())}")
            
            st.success("Campaign Ready for Deployment")
            
            st.markdown("#### 🧪 Test Flight")
            t_col1, t_col2 = st.columns([3,1])
            with t_col1:
                test_email = st.text_input("Test Email Address")
            with t_col2:
                st.write("")
                st.write("")
                if st.button("Send Test"):
                    if test_email and 'sequence' in st.session_state:
                        mailer = Mailer()
                        first = st.session_state['sequence'][0]
                        mailer.send_email(test_email, f"[TEST] {first['subject']}", first['body'])
                        st.toast(f"Sent to {test_email}")

            st.divider()
            
            
            if st.button("🚀 LAUNCH CAMPAIGN (Send to 'New' Leads)", type="primary"):
                 # ... existing launch logic ...
                 st.info("Initializing Launch Sequence...")
                 mailer = Mailer()
                 # Reuse existing logic but simplified
                 leads = load_data("leads")
                 new_leads = leads[leads['status'] == 'new']
                 
                 if new_leads.empty:
                     st.warning("No new leads found.")
                 else:
                     progress_bar = st.progress(0)
                     for i, row in new_leads.iterrows():
                         email_addr = row['email']
                         # status_text.text(f"Sending to {email_addr}...") # Optional: Add status text container
                         
                         # Personalization
                         subject = st.session_state['sequence'][0]['subject']
                         body = st.session_state['sequence'][0]['body']
                         
                         contact = row.get('contact_person') or "there"
                         biz = row.get('business_type') or "your business"
                         
                         subject = subject.replace("{contact_person}", str(contact)).replace("{business_name}", str(biz))
                         body = body.replace("{contact_person}", str(contact)).replace("{business_name}", str(biz))
                         
                         try:
                            if mailer.send_email(email_addr, subject, body):
                                from database import mark_contacted
                                mark_contacted(email_addr)
                            else:
                                pass # Failed count handled in full impl if needed
                         except Exception as e:
                            print(f"Send error: {e}")
                            
                         time.sleep(0.5)
                         progress_bar.progress((i+1)/len(new_leads))
                     st.balloons()
                     st.success("Campaign Complete!")

            if st.button("Start New Campaign"):
                 st.session_state['campaign_step'] = 0
                 st.session_state.pop('pain_points', None)
                 st.session_state.pop('sequence', None)
                 st.rerun()

    elif choice == "Agent Lab":
        st.header("🧪 Agent Lab")
        st.write("Interact with individual agents to test their capabilities.")
        
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs(["Researcher", "Qualifier", "Copywriter", "Reviewer", "Syntax", "UX", "Manager", "Designer"])
        
        with tab1:
            st.subheader("🕵️‍♀️ Researcher Agent")
            st.caption("Finds leads and gathers deep info.")
            res_mode = st.radio("Mode", ["Search Query", "Deep Scrape URL"], horizontal=True)
            res_input = st.text_input("Input", placeholder="e.g. 'Marketing agencies in Miami' or 'https://example.com'")
            
            if st.button("Run Research"):
                if res_input:
                    with st.spinner("Researching..."):
                        agent = ResearcherAgent()
                        context = {}
                        if res_mode == "Search Query":
                            context["query"] = res_input
                        else:
                            context["url"] = res_input
                            
                        # Async run wrapper
                        result = asyncio.run(agent.gather_intel(context))
                        st.json(result)

        with tab2:
            st.subheader("🛡️ Qualifier Agent")
            st.caption("Evaluates if a lead matches the ICP.")
            q_html = st.text_area("Lead Data (HTML or Text)", height=150, placeholder="Paste raw text or html here...")
            q_icp = st.text_area("ICP Criteria", value="Must Have: B2B, US-based\nDeal Breaker: Student, Non-profit")
            
            if st.button("Run Qualification"):
                if q_html:
                    with st.spinner("Qualifying..."):
                        agent = QualifierAgent()
                        # Context construction
                        ctx = f"Data: {q_html[:2000]}...\nCriteria: {q_icp}"
                        result = agent.think(ctx)
                        st.json(result)

        with tab3:
            st.subheader("✍️ Copywriter Agent")
            st.caption("Drafts cold emails.")
            c_info = st.text_area("Lead Info", value="Business: Tech Startup\nContact: John Doe\nPain: Manual data entry")
            c_prop = st.text_area("Value Prop", value="We automate data entry with AI.")
            
            if st.button("Write Copy"):
                with st.spinner("Drafting..."):
                    agent = CopywriterAgent()
                    ctx = f"Lead: {c_info}\nValue Prop: {c_prop}"
                    result = agent.think(ctx)
                    st.json(result)
                    if result and isinstance(result, dict):
                        st.markdown(f"**Subject:** {result.get('subject_line')}")
                        st.markdown(result.get('body'))

        with tab4:
            st.subheader("⚖️ Reviewer Agent")
            st.caption("Critiques content.")
            r_content = st.text_area("Content to Review", height=150)
            
            if st.button("Critique"):
                with st.spinner("Reviewing..."):
                    agent = ReviewerAgent()
                    result = agent.think(r_content)
                    st.json(result)

        with tab5:
            st.subheader("🔧 Syntax Agent")
            st.caption("Fixes structure and grammar.")
            s_content = st.text_area("Content to Fix", value="Hello [Name], we are from {{Company}}.")
            
            if st.button("Fix Syntax"):
                with st.spinner("Fixing..."):
                    agent = SyntaxAgent()
                    result = agent.think(s_content)
                    st.json(result)

        with tab6:
            st.subheader("🎨 UX Agent")
            st.caption("Suggests visualizations.")
            ux_data = st.text_area("Data JSON", value='{"revenue": [10, 20, 30], "month": ["Jan", "Feb", "Mar"]}')
            
            if st.button("Suggest UI"):
                with st.spinner("Designing..."):
                    agent = UXAgent()
                    result = agent.think(ux_data)
                    st.json(result)

        with tab7:
            st.subheader("👔 Manager Agent")
            st.caption("Autonomous Orchestrator.")
            m_goal = st.text_input("Goal", value="Find 3 leads for a SEO agency in Chicago")
            
            if st.button("Run Mission"):
                with st.spinner("Executing Mission... (This may take a minute)"):
                    manager = ManagerAgent()
                    result = asyncio.run(manager.run_mission(m_goal))
                    st.json(result)

        with tab8:
            st.subheader("🎨 Graphics Designer Agent")
            st.caption("Generates free AI images.")
            d_concept = st.text_input("Image Concept", value="Modern minimalist office workspace with plants, 8k resolution")
            
            if st.button("Generate Image"):
                with st.spinner("Dreaming up your image..."):
                    designer = GraphicsDesignerAgent()
                    result = designer.think(d_concept)
                    
                    st.image(result['image_url'], caption=result['revised_prompt'])
                    st.success("Image Generated!")
                    with st.expander("Debug Details"):
                        st.json(result)

    elif choice == "Settings":
        st.subheader("⚙️ Configuration")
        
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'config.yaml')

        # Helper to update .env
        def update_env(key, value):
            # Update current process logic immediately
            os.environ[key] = value
            
            lines = []
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    lines = f.readlines()
            
            key_found = False
            new_lines = []
            for line in lines:
                if line.startswith(f"{key}="):
                    new_lines.append(f"{key}={value}\n")
                    key_found = True
                else:
                    new_lines.append(line)
            
            if not key_found:
                new_lines.append(f"\n{key}={value}\n")
            
            with open(env_path, 'w') as f:
                f.writelines(new_lines)

        # Helper to update config.yaml
        def update_config(section, key, value):
            import yaml
            with open(config_path, 'r') as f:
                data = yaml.safe_load(f) or {}
            
            if section not in data:
                data[section] = {}
            data[section][key] = value
            
            with open(config_path, 'w') as f:
                yaml.dump(data, f, sort_keys=False)
            
            # Reload memory
            reload_config()

        settings_tab1, settings_tab2, settings_tab3, settings_tab4 = st.tabs(["🔑 API Keys", "🧠 LLM Settings", "📧 Email Settings", "🔍 Search Settings"])

        with settings_tab1:
            st.markdown("### Safe Storage (.env)")
            # ... (keep existing)

        # ... (keep existing tabs 2 & 3)

        with settings_tab4:
            st.markdown("### Search Engine Configuration")
            st.info("Configure your local SearXNG instance.")
            
            current_searx_url = config.get('search', {}).get('searxng_url', 'http://localhost:8081/search')
            new_searx_url = st.text_input("SearXNG URL", value=current_searx_url)
            
            current_depth = config.get('search', {}).get('default_depth', 1)
            new_depth = st.number_input("Crawl Depth", min_value=0, max_value=3, value=current_depth)
            
            current_max = config.get('search', {}).get('max_results', 50)
            new_max = st.number_input("Max Results", min_value=1, max_value=10000, value=current_max)

            if st.button("Update Search Config"):
                update_config('search', 'max_results', int(new_max))
                st.success("Search Configuration Updated!")
                time.sleep(1)
                st.rerun()

            st.divider()
            
            st.markdown("### ⚡ Concurrency & Throttling")
            st.info("Control how many leads are processed simultaneously.")
            
            current_concurrency = config.get('search', {}).get('concurrency', 20)
            
            # Color-coded slider logic
            slider_color = "red" if current_concurrency > 30 else "orange" if current_concurrency > 20 else "green"
            
            new_concurrency = st.slider(
                "Parallel Tasks Limit", 
                min_value=1, 
                max_value=100, 
                value=current_concurrency,
                help="Safe: 10-30. Caution: 30-50. Danger Zone: 50+ (High risk of rate limits)"
            )
            
            if new_concurrency > 50:
                 st.error("🔥 DANGER ZONE: Extremely high concurrency. You will likely trigger DDoS protection on target sites or bans from Google/Bing.")
            elif new_concurrency > 30:
                 st.warning("⚠️ High Concurrency: Make sure you have high-quality rotating proxies or enterprise API keys.")
            else:
                 st.success("✅ Safe Concurrency Level")
                 
            if st.button("Update Throttling"):
                update_config('search', 'concurrency', int(new_concurrency))
                st.success(f"Concurrency set to {new_concurrency} parallel tasks.")
                time.sleep(1)
                st.rerun()

            st.divider()
            st.markdown("### 🎭 Search Profiles")
            st.info("Manage presets for different search strategies.")
            
            # Load current profiles
            current_profiles = config.get('search', {}).get('profiles', {})
            profile_names = list(current_profiles.keys())
            
            # Master-Detail Selection
            col_p1, col_p2 = st.columns([1, 2])
            
            with col_p1:
                selected_profile_name = st.radio("Select Profile", ["+ Create New"] + profile_names, label_visibility="collapsed")
            
            with col_p2:
                with st.container():
                    st.markdown(f'<div class="css-card">', unsafe_allow_html=True)
                    
                    # Determine if creating new
                    is_new = selected_profile_name == "+ Create New"
                    
                    if is_new:
                        edit_name = st.text_input("New Profile Name", placeholder="e.g., crypto_startups")
                        edit_cats = []
                        edit_engines = []
                    else:
                        edit_name = selected_profile_name
                        data = current_profiles.get(selected_profile_name, {})
                        edit_cats = data.get('categories', [])
                        edit_engines = data.get('engines', [])
                    
                    # Known Options (Superset)
                    KNOWN_CATS = sorted(list(set(edit_cats + ["general", "it", "science", "social media", "news", "images", "videos", "files", "map", "music"])))
                    KNOWN_ENGINES = sorted(list(set(edit_engines + ["google", "bing", "duckduckgo", "yahoo", "startpage", "wikidata", "wikipedia", "reddit", "twitter", "linkedin", "github", "stackoverflow"])))
                    
                    # Editors
                    new_cats = st.multiselect("Categories", KNOWN_CATS, default=edit_cats)
                    new_engines = st.multiselect("Engines", KNOWN_ENGINES, default=edit_engines)
                    
                    # Custom Inputs (for things not in known list)
                    custom_engines = st.text_input("Add Custom Engines (comma separated)", help="e.g. brave, qwant")
                    if custom_engines:
                        extras = [e.strip() for e in custom_engines.split(",") if e.strip()]
                        new_engines.extend(extras)

                    st.markdown("---")
                    
                    # Actions
                    col_save, col_del = st.columns(2)
                    with col_save:
                        if st.button(f"💾 Save '{edit_name}'"):
                            if not edit_name:
                                st.error("Name required.")
                            else:
                                # Update Logic
                                updated_profiles = current_profiles.copy()
                                updated_profiles[edit_name] = {
                                    "categories": new_cats,
                                    "engines": list(set(new_engines)) # Dedupe
                                }
                                update_config('search', 'profiles', updated_profiles)
                                st.success(f"Profile '{edit_name}' saved!")
                                time.sleep(1)
                                st.rerun()
                                
                    with col_del:
                        if not is_new and st.button("🗑️ Delete Profile"):
                            updated_profiles = current_profiles.copy()
                            if edit_name in updated_profiles:
                                del updated_profiles[edit_name]
                                update_config('search', 'profiles', updated_profiles)
                                st.warning(f"Profile '{edit_name}' deleted.")
                                time.sleep(1)
                                st.rerun()

                    st.markdown('</div>', unsafe_allow_html=True)

        st.divider()
        st.markdown("**Raw Config View**")
        with open(config_path, 'r') as f:
            st.code(f.read(), language='yaml')
        st.info("Keys are stored locally in the .env file.")
        
        st.markdown("#### 🤖 LLM Providers")
        
        key_urls = {
            "GEMINI_API_KEY": "https://aistudio.google.com/app/apikey",
            "OPENAI_API_KEY": "https://platform.openai.com/api-keys",
            "OPENROUTER_API_KEY": "https://openrouter.ai/keys",
            "MISTRAL_API_KEY": "https://console.mistral.ai/api-keys/",
            "GROQ_API_KEY": "https://console.groq.com/keys",
            "COHERE_API_KEY": "https://dashboard.cohere.com/api-keys",
            "NVIDIA_API_KEY": "https://build.nvidia.com/",
            "CEREBRAS_API_KEY": "https://cloud.cerebras.ai/",
            "HUGGINGFACE_API_KEY": "https://huggingface.co/settings/tokens",
            "GITHUB_TOKEN": "https://github.com/settings/tokens",
            "CLOUDFLARE_API_KEY": "https://dash.cloudflare.com/profile/api-tokens",
            "RESEND_API_KEY": "https://resend.com/api-keys",
            "BREVO_API_KEY": "https://app.brevo.com/settings/keys/api",
            "SENDGRID_API_KEY": "https://app.sendgrid.com/settings/api_keys"
        }

        llm_keys = [
            "GEMINI_API_KEY", "OPENAI_API_KEY", "OLLAMA_API_KEY", "OPENROUTER_API_KEY", 
            "MISTRAL_API_KEY", "GROQ_API_KEY", "COHERE_API_KEY",
            "NVIDIA_API_KEY", "CEREBRAS_API_KEY", "HUGGINGFACE_API_KEY",
            "GITHUB_TOKEN", "CLOUDFLARE_API_KEY"
        ]
        
        for key in llm_keys:
            col_btn, col_input = st.columns([1, 4])
            url = key_urls.get(key)
            with col_btn:
                st.markdown(f"<br>[Get Key]({url})", unsafe_allow_html=True)
            with col_input:
                current_val = os.getenv(key, "")
                new_val = st.text_input(key, value=current_val, type="password")
                if new_val != current_val:
                    if st.button(f"Save {key}"):
                        update_env(key, new_val)
                        st.success(f"Saved {key}! Please restart to apply.")
        
        st.divider()
        st.markdown("#### 📧 Email Services")
        email_keys = [
            "RESEND_API_KEY", "BREVO_API_KEY", "SENDGRID_API_KEY"
        ]
        
        for key in email_keys:
            col_btn, col_input = st.columns([1, 4])
            url = key_urls.get(key)
            with col_btn:
                 st.markdown(f"<br>[Get Key]({url})", unsafe_allow_html=True)
            with col_input:
                current_val = os.getenv(key, "")
                new_val = st.text_input(key, value=current_val, type="password")
                if new_val != current_val:
                    if st.button(f"Save {key}"):
                        update_env(key, new_val)
                        st.success(f"Saved {key}! Please restart to apply.")

        with settings_tab2:
            st.markdown("### AI Brain Configuration")
            
            current_provider = config.get('llm', {}).get('provider', 'gemini')
            current_model = config.get('llm', {}).get('model_name', '')
            
            llm_providers = [
                'gemini', 'openai', 'ollama', 'openrouter', 
                'mistral', 'groq', 'cohere', 'nvidia', 'cerebras', 'huggingface', 'github_models', 'cloudflare'
            ]
            
            # Common models for each provider
            PROVIDER_MODELS = {
                'gemini': ['gemini-flash-latest', 'gemini-pro', 'gemini-1.5-flash', 'gemini-1.5-pro'],
                'openai': ['gpt-4o-mini', 'gpt-4o', 'gpt-3.5-turbo'],
                'ollama': ['llama3', 'llama3:70b', 'mistral', 'phi3'], 
                'mistral': ['mistral-large-latest', 'mistral-small-latest', 'codestral-latest'],
                'groq': ['llama3-70b-8192', 'llama3-8b-8192', 'mixtral-8x7b-32768', 'gemma-7b-it'],
                'cohere': ['command-r', 'command-r-plus'],
                'nvidia': ['meta/llama3-70b-instruct', 'microsoft/phi-3-mini-128k-instruct'],
                'cerebras': ['llama3.1-70b', 'llama3.1-8b'],
                'github_models': ['Phi-3-mini-4k-instruct', 'Mistral-large', 'Llama-3.2-90B-Vision'],
                'cloudflare': ['@cf/meta/llama-3-8b-instruct', '@cf/meta/llama-3.1-8b-instruct'],
                'huggingface': ['meta-llama/Meta-Llama-3-8B-Instruct', 'mistralai/Mistral-7B-Instruct-v0.2'],
                'openrouter': ['openai/gpt-4o-mini', 'google/gemini-flash-1.5', 'meta-llama/llama-3.1-70b-instruct']
            }

            previous_provider = st.session_state.get('prev_provider', current_provider)
            
            if previous_provider != current_provider:
                 # Provider changed externally or reloaded
                 pass

            new_provider = st.selectbox("LLM Provider", llm_providers, index=llm_providers.index(current_provider) if current_provider in llm_providers else 0)
            
            # Update session state for provider change tracking
            st.session_state['prev_provider'] = new_provider

            # Special Config for Ollama
            if new_provider == 'ollama':
                current_base_url = config.get('llm', {}).get('ollama_base_url', 'http://localhost:11434')
                new_base_url = st.text_input("Ollama Base URL", value=current_base_url, help="Local: http://localhost:11434 | Cloud: https://ollama.com")
                if new_base_url != current_base_url:
                    if st.button("Save Ollama URL"):
                        update_config('llm', 'ollama_base_url', new_base_url)
                        st.success("Ollama URL Saved!")
                        time.sleep(1)
                        st.rerun()

            # Model Selection Logic
            
            # Initialize custom lists in session state if not present
            if 'custom_model_lists' not in st.session_state:
                st.session_state['custom_model_lists'] = {}

            # Check if we have a custom list for this provider
            fetched_list = st.session_state['custom_model_lists'].get(new_provider)
            
            # Combine hardcoded defaults with fetched (or overwrite)
            # Strategy: Use fetched if available, else hardcoded
            if fetched_list:
                known_models = fetched_list
            else:
                known_models = PROVIDER_MODELS.get(new_provider, [])
            
            # Refresh Button
            col_sel, col_ref = st.columns([4, 1])
            with col_sel:
                # Decide index for curr_model in list
                model_options = known_models + ["Other (Custom)..."]
                
                default_index = 0
                if current_model in known_models and new_provider == current_provider:
                    default_index = known_models.index(current_model)
                elif current_model not in known_models and new_provider == current_provider and current_model:
                    default_index = len(known_models) # "Other"
                
                selected_model_option = st.selectbox(
                    "Model Selection", 
                    model_options, 
                    index=default_index,
                    help="Select a preset model or choose 'Other' to type your own."
                )
            
            with col_ref:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🔄 Refresh"):
                    from model_fetcher import fetch_models_for_provider
                    with st.spinner(f"Fetching models for {new_provider}..."):
                        models = fetch_models_for_provider(new_provider)
                        if models:
                            st.session_state['custom_model_lists'][new_provider] = models
                            st.success(f"Found {len(models)} models!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.warning("Could not fetch models. check API Key.")



                if st.button("🆓 Scan for FREE Models"):
                    from model_fetcher import get_free_models_for_provider
                    with st.spinner(f"Scanning for free models on {new_provider}..."):
                        free_models = get_free_models_for_provider(new_provider)
                        if free_models:
                            st.session_state['custom_model_lists'][new_provider] = free_models
                            st.success(f"Found {len(free_models)} FREE models! List updated.")
                            with st.expander("View Free Models", expanded=True):
                                st.write(free_models)
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.warning(f"No specific 'free' models found for {new_provider} (or API key missing).")

                st.markdown("---")
                st.markdown("### ⚡ Free Mode Configuration")
                
                router_strategy = st.radio(
                    "Load Balancing Strategy",
                    ["priority", "random"],
                    format_func=lambda x: "Priority (Sequential - Best for consistency)" if x == "priority" else "Random (Spread Load - Best for Rate Limits)",
                    help="Priority: Always tries first model, then second, etc. Random: Shuffles order per request."
                )
                
                if st.button("⚡ Auto-Configure ALL Free Models"):
                    from model_fetcher import scan_all_free_providers
                    with st.spinner("Scanning ALL providers for free models..."):
                        candidates = scan_all_free_providers()
                        
                        if candidates:
                            # 1. Update Config to Router Mode
                            update_config('llm', 'mode', 'router')
                            update_config('llm', 'provider', 'gemini') # Default fallback
                            
                            # 2. Update Router Candidates
                            # Need nested update, so we read, modify, write manually to be safe or use helper if capable
                            # The helper `update_config` does shallow merge on section.
                            # We need to update `llm.router.candidates`
                            
                            import yaml
                            with open(config_path, 'r') as f:
                                full_config = yaml.safe_load(f) or {}
                                
                            if 'llm' not in full_config: full_config['llm'] = {}
                            if 'router' not in full_config['llm']: full_config['llm']['router'] = {}
                            
                            full_config['llm']['router']['candidates'] = candidates
                            full_config['llm']['router']['strategy'] = router_strategy
                            full_config['llm']['mode'] = 'router'
                            
                            with open(config_path, 'w') as f:
                                yaml.dump(full_config, f, sort_keys=False)
                                
                            reload_config()
                            
                            st.success(f"✅ Configuration Updated! Found {len(candidates)} free models. Strategy: {router_strategy}")
                            
                            # Tally Count
                            counts = {}
                            for c in candidates:
                                p = c.get('provider', 'Unknown')
                                counts[p] = counts.get(p, 0) + 1
                            
                            cols = st.columns(len(counts))
                            for idx, (provider, count) in enumerate(counts.items()):
                                cols[idx].metric(label=provider.title(), value=count)

                            st.caption(f"Mode set to **Router ({router_strategy})**. The system will now automatically switch/shuffle between these models.")
                            with st.expander("View Active Candidate List", expanded=True):
                                st.write(candidates)
                            time.sleep(2)
                            st.rerun()
                        else:
                            st.error("No free models found! Check your API Keys in .env")

            if selected_model_option == "Other (Custom)...":
                final_model_name = st.text_input("Enter Custom Model Name", value=current_model if current_model not in known_models else "")
            else:
                final_model_name = selected_model_option

            if st.button("Update LLM Config"):
                if final_model_name:
                    update_config('llm', 'provider', new_provider)
                    update_config('llm', 'model_name', final_model_name)
                    st.success(f"Updated! Provider: {new_provider}, Model: {final_model_name}")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Please provide a model name.")

        with settings_tab3:
            st.markdown("### Email Routing")
            
            current_email_provider = config.get('email', {}).get('provider', 'smtp')
            email_providers = ['smart', 'resend', 'brevo', 'sendgrid', 'smtp']
            
            new_email_provider = st.selectbox("Active Email Service", email_providers, index=email_providers.index(current_email_provider) if current_email_provider in email_providers else 0)
            
            if st.button("Update Email Config"):
                 update_config('email', 'provider', new_email_provider)
                 st.success("Email Configuration Updated!")
                 time.sleep(1)
                 st.rerun()
            
            st.divider()
            st.markdown("**Raw Config View**")
            with open(config_path, 'r') as f:
                st.code(f.read(), language='yaml')

if __name__ == '__main__':
    main()
