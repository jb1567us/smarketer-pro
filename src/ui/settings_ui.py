import streamlit as st
import os
import time
import json
import yaml
import asyncio
import psutil
from config import config, reload_config
from database import (
    get_platform_credentials, save_platform_credential, delete_platform_credential, 
    get_platform_credentials, save_platform_credential, delete_platform_credential, 
    get_captcha_settings, save_captcha_settings, get_setting, save_setting
)
from model_fetcher import fetch_models_for_provider, scan_all_free_providers
from utils.captcha_solver import CaptchaSolver

def get_system_usage():
    """Returns current CPU and RAM usage."""
    try:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        return cpu, ram
    except Exception:
        return 0, 0

def render_settings_page():
    st.header("⚙️ Configuration")
    
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config.yaml')

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
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f) or {}
        
        if section not in data:
            data[section] = {}
        data[section][key] = value
        
        with open(config_path, 'w') as f:
            yaml.dump(data, f, sort_keys=False)
        
        # Reload memory
        reload_config()

    settings_tab1, settings_tab2, settings_tab3, settings_tab4, settings_tab5, settings_tab6, settings_tab7 = st.tabs(["🏢 General", "🔑 API Keys", "🧠 LLM Settings", "📧 Email Settings", "🔍 Search Settings", "📱 Platforms", "🛡️ Captcha Solver"])

    with settings_tab1:
            st.subheader("Global Preferences")
            
            # --- APP MODE TOGGLE ---
            st.markdown("### 🔄 Application Mode")
            st.caption("Switch between B2B (Sales/Deals) and B2C (Growth/Virality) interfaces.")
            
            current_mode = get_setting("app_mode", "B2B")
            new_mode = st.radio("Active Mode", ["B2B", "B2C"], index=0 if current_mode == "B2B" else 1, horizontal=True)
            
            if new_mode != current_mode:
                save_setting("app_mode", new_mode)
                st.session_state["app_mode"] = new_mode
                st.success(f"Switched to {new_mode} mode! Reloading...")
                time.sleep(1)
                st.rerun()

    with settings_tab2:
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

    with settings_tab3:
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
        
        new_provider = st.selectbox("LLM Provider", llm_providers, index=llm_providers.index(current_provider) if current_provider in llm_providers else 0)
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
                with st.spinner(f"Fetching models for {new_provider}..."):
                    models = asyncio.run(fetch_models_for_provider(new_provider))
                    if models:
                        st.session_state['custom_model_lists'][new_provider] = models
                        st.success(f"Found {len(models)} models!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.warning("Could not fetch models. check API Key.")

        st.markdown("---")
        st.markdown("### ⚡ Free Mode Configuration")
        router_strategy = st.radio("Load Balancing Strategy", ["priority", "random"])
        
        if st.button("🆓 Scan for FREE Models"):
            with st.spinner("Scanning ALL providers for free models..."):
                candidates = asyncio.run(scan_all_free_providers())
                
                if candidates:
                    # 1. Update Config to Router Mode
                    update_config('llm', 'mode', 'router')
                    update_config('llm', 'provider', 'gemini') # Default fallback
                    
                    # 2. Update Router Candidates
                    # Need nested update, so we read, modify, write manually to be safe or use helper if capable
                    # The helper `update_config` does shallow merge on section.
                    # We need to update `llm.router.candidates`
                    
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

    with settings_tab4:
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

    with settings_tab5:
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
            update_config('search', 'searxng_url', new_searx_url) # Added this line
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

    with settings_tab6:
        st.markdown("### 🔗 SEO Platform Hub")
        st.caption("Manage credentials for automated backlink submissions.")
        
        platforms = ["WordPress", "Blogger", "Tumblr", "Reddit", "Medium", "Quora", "Wix", "Ghost", "Substack", "Weebly"]
        selected_plat = st.selectbox("Select Platform to Configure", platforms)
        
        creds = get_platform_credentials(selected_plat.lower())
        
        with st.form(f"creds_{selected_plat}"):
            user = st.text_input("Username / Email", value=creds.get('username', '') if creds else "")
            pwd = st.text_input("Password / App Password", value=creds.get('password', '') if creds else "", type="password")
            api = st.text_input("API Key (if applicable)", value=creds.get('api_key', '') if creds else "", type="password")
            
            # Extra meta (e.g. blog ID)
            current_meta = creds.get('meta_json', '{}') if creds else '{}'
            meta_str = st.text_area("Extra Config (JSON)", value=current_meta)
            
            if st.form_submit_button(f"Save {selected_plat} Credentials"):
                try:
                    # Validate JSON
                    if meta_str: json.loads(meta_str)
                    save_platform_credential(selected_plat.lower(), user, pwd, api, meta_str)
                    st.success(f"Credentials for {selected_plat} saved!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")

        st.divider()
        st.subheader("Active Integrations")
        all_creds = get_platform_credentials()
        if not all_creds:
            st.info("No platforms configured yet.")
        else:
            for c in all_creds:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"✅ **{c['platform_name'].title()}** ({c['username']})")
                with col2:
                    if st.button("Delete", key=f"del_cred_{c['id']}"):
                        delete_platform_credential(c['platform_name'])
                        st.rerun()

    with settings_tab7:
        st.markdown("## 🛡️ Captcha Solver Settings")
        st.caption("Enable and configure an external or local Captcha solving service.")
        
        c_settings = get_captcha_settings()
        
        # --- Resource Monitor (Always show if possible) ---
        with st.expander("📊 AI Resource Monitor", expanded=True):
            cpu, ram = get_system_usage()
            col_r1, col_r2 = st.columns(2)
            col_r1.metric("CPU Usage", f"{cpu}%")
            col_r2.metric("RAM Usage", f"{ram}%")
            if cpu > 80: st.warning("High CPU! AI operations may be slow.")
        
        st.divider()
        
        c_enabled = st.toggle("Enable Captcha Solver", value=bool(c_settings['enabled']))
        
        # page_selection = st.sidebar.radio(...) # REMOVED as it belongs in app.py logic, not settings
        
        providers = ["none", "2captcha", "anticaptcha", "capsolver", "deathbycaptcha", "bestcaptchasolver", "local-whisper"]
        current_provider = c_settings['provider']
        default_provider_idx = providers.index(current_provider) if current_provider in providers else 0
        
        c_provider = st.selectbox("Captcha Provider", providers, index=default_provider_idx)
        
        if c_provider == "local-whisper":
            st.info("🤖 **Local Whisper Mode**: Uses your own hardware. No API key needed for audio challenges.")
            st.warning("Ensure `ffmpeg` is installed on your system.")
            c_api_key = "LOCAL_USE" # Placeholder
        else:
            c_api_key = st.text_input("Service API Key", value=c_settings['api_key'], type="password")

        if st.button("Save Captcha Settings"):
            save_captcha_settings(c_provider, c_api_key, c_enabled)
            st.success("✅ Captcha settings saved!")
            time.sleep(1)
            st.rerun()

        if c_enabled and c_api_key and c_provider != "local-whisper" and c_provider != "none":
            solver = CaptchaSolver(c_provider, c_api_key)
            with st.spinner("Checking balance..."):
                balance = asyncio.run(solver.get_balance())
                if balance: st.metric("Current Balance", balance)
