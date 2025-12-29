import streamlit as st
import pandas as pd
import sqlite3
import os
import sys
import asyncio
import time
from dotenv import load_dotenv

load_dotenv()

# Ensure src is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_connection, get_pain_points, save_template, get_templates, init_db
from workflow import run_outreach
from campaign_manager import start_campaign_step_research, start_campaign_step_copy, start_campaign_step_send
from config import config

st.set_page_config(page_title="B2B Outreach Agent", layout="wide")

def load_data(table):
    conn = get_connection()
    df = pd.read_sql_query(f"SELECT * from {table}", conn)
    conn.close()
    return df

def main():
    st.title("🚀 B2B Outreach Agent")

    menu = ["Dashboard", "Lead Discovery", "Campaign Manager", "Settings"]
    choice = st.sidebar.selectbox("Navigation", menu)

    if choice == "Dashboard":
        st.subheader("Overview")
        try:
            leads = load_data("leads")
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Leads", len(leads))
            col2.metric("Nurtured", len(leads[leads['status'] == 'nurtured']))
            col3.metric("Pending", len(leads[leads['status'] == 'new']))
            
            st.dataframe(leads)
        except Exception as e:
            st.error(f"Error loading dashboard: {e}")
            if st.button("Initialize Database"):
                init_db()
                st.success("Database initialized.")

    elif choice == "Lead Discovery":
        st.subheader("🔍 Find New Leads")
        with st.form("search_form"):
            query = st.text_input("Search Query", "marketing agencies in Austin")
            niche = st.text_input("Target Niche Filter (Optional)", "Marketing")
            profile = st.selectbox("Search Profile", ["default", "tech", "creative", "news"])
            submitted = st.form_submit_button("Start Search")
            
            if submitted:
                st.info("Running search agent... Check the terminal for live logs.")
                # Async wrapper
                asyncio.run(run_outreach(query, profile_name=profile, target_niche=niche))
                st.success("Search complete!")
                st.rerun()

    elif choice == "Campaign Manager":
        st.subheader("📬 Smart Nurture Campaigns")
        
        tab1, tab2 = st.tabs(["Research & Strategy", "Launch Campaign"])
        
        with tab1:
            st.markdown("### 1. Research Pain Points")
            niche_input = st.text_input("Niche", "Interior Design")
            if st.button("Analyze Niche"):
                with st.spinner("AI Researcher is thinking..."):
                    # We need to expose research_niche from researcher.py
                    # Implemented via wrapper below
                    points = start_campaign_step_research(niche_input)
                    st.session_state['pain_points'] = points
            
            if 'pain_points' in st.session_state:
                st.write("Found Pain Points:")
                selected_pain = st.radio("Select a Pain Point to target:", 
                                         [p['title'] for p in st.session_state['pain_points']])
                
                st.markdown("### 2. Generate Content")
                product_name = st.text_input("Product Name")
                product_desc = st.text_input("Product Description")
                
                if st.button("Generate Email Sequence"):
                    # Find full object
                    pain_obj = next(p for p in st.session_state['pain_points'] if p['title'] == selected_pain)
                    with st.spinner("AI Copywriter is writing..."):
                        seq = start_campaign_step_copy(niche_input, pain_obj, product_name, product_desc)
                        st.session_state['sequence'] = seq
                        st.success("Emails generated! Go to Launch tab.")

        with tab2:
            st.markdown("### 3. Review & Launch")
            if 'sequence' in st.session_state:
                for email in st.session_state['sequence']:
                    with st.expander(f"Stage: {email['stage'].upper()} - {email['subject']}"):
                        st.markdown(email['body'], unsafe_allow_html=True)
                
                if st.button("Confirm & Send to All 'New' Leads"):
                    st.warning("Sending emails requires SMTP setup.")
                    # In a real app, this would use the `campaign_manager` send logic
                    st.info("Simulation: Sending...")
                    time.sleep(2)
                    st.success("Campaign Started!")
            else:
                st.info("Generate content in the previous tab first.")

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

        settings_tab1, settings_tab2, settings_tab3 = st.tabs(["🔑 API Keys", "🧠 LLM Settings", "📧 Email Settings"])

        with settings_tab1:
            st.markdown("### Safe Storage (.env)")
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
                "GEMINI_API_KEY", "OPENAI_API_KEY", "OPENROUTER_API_KEY", 
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
                'mistral', 'groq', 'cohere', 'nvidia', 'cerebras'
            ]
            
            new_provider = st.selectbox("LLM Provider", llm_providers, index=llm_providers.index(current_provider) if current_provider in llm_providers else 0)
            new_model = st.text_input("Model Name", value=current_model, help="e.g. gpt-4o-mini, gemini-flash-latest, llama3")
            
            if st.button("Update LLM Config"):
                update_config('llm', 'provider', new_provider)
                update_config('llm', 'model_name', new_model)
                st.success("LLM Configuration Updated!")
                time.sleep(1)
                st.rerun()

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
