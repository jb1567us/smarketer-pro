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

from database import get_connection, get_pain_points, save_template, get_templates, init_db, clear_all_leads, delete_leads
from workflow import run_outreach
from campaign_manager import start_campaign_step_research, start_campaign_step_copy, start_campaign_step_send
from config import config, reload_config

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
            
            # Add selection column for deletion
            leads['Select'] = False
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

                with m_col2:
                    # Export CSV
                    csv = leads.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name='leads_export.csv',
                        mime='text/csv',
                    )
                
                st.divider()
                st.caption("To delete specific leads, use the SQLite database directly or clear all above.")

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
            
            # Reload memory
            reload_config()

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
