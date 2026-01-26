import streamlit as st
import os
import yaml
import time
import asyncio
from config import config, reload_config
from ui.components import confirm_action, safe_action_wrapper, premium_header, render_page_chat
from agents import ManagerAgent
from model_fetcher import scan_all_free_providers

def render_settings_page():
    premium_header("⚙️ Configuration", "Manage your enterprise API keys, routing strategies, and system global settings.")
    
    # Paths (Robust resolution)
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    env_path = os.path.join(base_dir, '.env')
    config_path = os.path.join(base_dir, 'config.yaml')

    # Helper to update .env
    def update_env(key, value):
        env_vars = {}
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                for line in f:
                    if '=' in line:
                        k, v = line.strip().split('=', 1)
                        env_vars[k] = v
        
        env_vars[key] = value
        
        with open(env_path, 'w') as f:
            for k, v in env_vars.items():
                f.write(f'{k}={v}\n')
        
        os.environ[key] = value # Update current session
        
    # Helper to update config.yaml
    def update_config(section, key, value):
        with open(config_path, 'r') as f:
            full_config = yaml.safe_load(f) or {}
            
        if section not in full_config:
            full_config[section] = {}
            
        full_config[section][key] = value
        
        with open(config_path, 'w') as f:
            yaml.dump(full_config, f, sort_keys=False)
            
        reload_config()

    settings_tab1, settings_tab2, settings_tab3, settings_tab4 = st.tabs(["🏢 General", "🔑 API Keys", "🧠 LLM Settings", "📧 Email Settings"])

    with settings_tab1:
        st.subheader("General Preferences")
        st.info("Global application settings will appear here.")
        # Placeholder for future general settings (Theme, Timezone, etc.)

    with settings_tab2:
        st.subheader("🔑 API Key Management")
        st.markdown("""
        Configure your external service connections here. **System** uses these keys to power the AI agents, 
        send outreach emails, and manage landing pages. 
        
        > [!NOTE]
        > Keys are stored locally in your `.env` file and are never sent to our servers.
        """)
        
        # Link Map for "Get Key"
        key_links = {
            "OPENAI_API_KEY": "https://platform.openai.com/api-keys",
            "ANTHROPIC_API_KEY": "https://console.anthropic.com/settings/keys",
            "GEMINI_API_KEY": "https://aistudio.google.com/app/apikey",
            "CLOUDFLARE_API_KEY": "https://dash.cloudflare.com/profile/api-tokens",
            "RESEND_API_KEY": "https://resend.com/api-keys",
            "BREVO_API_KEY": "https://app.brevo.com/settings/keys/api",
            "SENDGRID_API_KEY": "https://app.sendgrid.com/settings/api_keys",
            "MAILJET_API_KEY": "https://app.mailjet.com/account/api_keys",
            "MAILJET_SECRET_KEY": "https://app.mailjet.com/account/api_keys",
            "MAILGUN_API_KEY": "https://app.mailgun.com/app/account/security/api_keys",
            "MAILGUN_DOMAIN": "https://app.mailgun.com/app/sending/domains",
            "POSTMARK_API_KEY": "https://account.postmarkapp.com/servers",
            "MAILERSEND_API_KEY": "https://app.mailersend.com/api-tokens",
            "SENDPULSE_EMAIL": "https://sendpulse.com/login",
            "SENDPULSE_SMTP_PASSWORD": "https://login.sendpulse.com/settings/#smtp",
            "AWS_ACCESS_KEY_ID": "https://console.aws.amazon.com/iam/home?#security_credential",
            "AWS_SECRET_ACCESS_KEY": "https://console.aws.amazon.com/iam/home?#security_credential",
            "AWS_REGION": "https://docs.aws.amazon.com/ses/latest/dg/regions.html",
            "MAILTRAP_API_TOKEN": "https://mailtrap.io/home",
            "ZOHO_ZEPTOMAIL_TOKEN": "https://zeptomail.zoho.com/",
            "NETCORE_API_KEY": "https://netcorecloud.com/",
            "OPENROUTER_API_KEY": "https://openrouter.ai/keys",
            "GROQ_API_KEY": "https://console.groq.com/keys",
            "MISTRAL_API_KEY": "https://console.mistral.ai/api-keys/",
            "HUGGINGFACE_API_KEY": "https://huggingface.co/settings/tokens",
            "GITHUB_TOKEN": "https://github.com/settings/tokens",
            "CEREBRAS_API_KEY": "https://cloud.cerebras.ai/",
            "NVIDIA_API_KEY": "https://build.nvidia.com/explore/discover",
            "COHERE_API_KEY": "https://dashboard.cohere.com/api-keys",
        }

        # Email Keys
        st.markdown("#### 📧 Email Services")
        email_keys = [
            "RESEND_API_KEY", "BREVO_API_KEY", "SENDGRID_API_KEY", 
            "MAILJET_API_KEY", "MAILJET_SECRET_KEY", 
            "MAILGUN_API_KEY", "MAILGUN_DOMAIN",
            "POSTMARK_API_KEY", 
            "MAILERSEND_API_KEY",
            "SENDPULSE_EMAIL", "SENDPULSE_SMTP_PASSWORD",
            "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_REGION",
            "MAILTRAP_API_TOKEN", "ZOHO_ZEPTOMAIL_TOKEN", "NETCORE_API_KEY"
        ]
        
        for key in email_keys:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                current_val = os.getenv(key, "")
                new_val = st.text_input(f"{key}", value=current_val, type="password", help=f"Enter your {key.replace('_', ' ').lower()}")
            with col2:
                if key in key_links:
                    st.markdown(f"\n\n[Get Key 🔗]({key_links[key]})")
            with col3:
                if new_val != current_val:
                    def save_key():
                        update_env(key, new_val)
                    
                    st.markdown("\n\n") 
                    confirm_action(
                        label=f"Save {key.split('_')[0]}",
                        prompt=f"Update {key} in .env?",
                        on_confirm=lambda: [save_key(), st.rerun()],
                        key=f"save_{key}"
                    )
        
        st.divider()
        st.markdown("#### 🧠 AI Models")
        llm_keys = [
            "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", 
            "OPENROUTER_API_KEY", "GROQ_API_KEY", "MISTRAL_API_KEY",
            "HUGGINGFACE_API_KEY", "GITHUB_TOKEN", "CEREBRAS_API_KEY",
            "NVIDIA_API_KEY", "COHERE_API_KEY", "CLOUDFLARE_ACCOUNT_ID", "CLOUDFLARE_API_KEY"
        ]
        for key in llm_keys:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                current_val = os.getenv(key, "")
                new_val = st.text_input(f"{key}", value=current_val, type="password", help=f"Enter your {key.replace('_', ' ').lower()}")
            with col2:
                if key in key_links:
                    st.markdown(f"\n\n[Get Key 🔗]({key_links[key]})")
            with col3:
                if new_val != current_val:
                    st.markdown("\n\n")
                    def save_llm_key():
                         update_env(key, new_val)
                    confirm_action(
                        label=f"Save {key.split('_')[0]}",
                        prompt=f"Update {key}?",
                        on_confirm=lambda: [save_llm_key(), st.rerun()],
                        key=f"save_{key}"
                    )

    with settings_tab3:
        st.subheader("🧠 LLM Infrastructure")
        
        col_mode, col_provider = st.columns(2)
        
        current_llm_mode = config.get('llm', {}).get('mode', 'single')
        new_llm_mode = col_mode.selectbox("LLM Mode", ["single", "router"], index=0 if current_llm_mode == 'single' else 1)
        
        # Auto-Scan Setting
        auto_scan = config.get('llm', {}).get('auto_scan', False)
        new_auto_scan = st.toggle("Auto-Scan for Free Models on Startup", value=auto_scan, help="Periodically checks for new free LLM models and adds them to your router.")
        if new_auto_scan != auto_scan:
            update_config('llm', 'auto_scan', new_auto_scan)
            st.toast("Auto-Scan setting updated.")
            time.sleep(0.5)
            st.rerun()
        
        if new_llm_mode == 'single':
            current_provider = config.get('llm', {}).get('provider', 'gemini')
            providers = ['gemini', 'openai', 'groq', 'mistral', 'openrouter', 'ollama', 'huggingface', 'cerebras', 'nvidia', 'cohere']
            new_provider = col_provider.selectbox("Default Provider", providers, index=providers.index(current_provider) if current_provider in providers else 0)
            
            if st.button("Save Single Mode Settings"):
                update_config('llm', 'mode', 'single')
                update_config('llm', 'provider', new_provider)
                st.success("LLM Configuration Updated!")
                st.rerun()
        else:
            st.info("🚀 **Smart Router Active**: Distributes requests across multiple providers for maximum resiliency.")
            
            # Router Candidates
            st.markdown("#### Active Router Candidates")
            
            # Get router status if available
            from llm.factory import LLMFactory
            router = LLMFactory.get_provider()
            router_status = {}
            if hasattr(router, 'get_status'):
                router_status = {(s['provider'], s['model']): s for s in router.get_status()}

            candidates = config.get('llm', {}).get('router', {}).get('candidates', [])
            
            if not candidates:
                st.warning("No candidates defined. The system will use defaults or fallback to Gemini.")
            else:
                for i, cand in enumerate(candidates):
                    c_col1, c_col2, c_tier, c_col3, c_col4 = st.columns([2, 2, 1, 1, 1])
                    c_col1.markdown(f"**{cand['provider'].upper()}**")
                    c_col2.markdown(f"`{cand['model_name']}`")
                    
                    tier = cand.get('tier', 'economy')
                    tier_icon = "⚡" if tier == 'performance' else "🪙"
                    c_tier.markdown(f"{tier_icon} {tier.title()}")
                    
                    # Health Indicator
                    p_key = (f"{cand['provider'].title()}Provider", cand['model_name'])
                    if p_key in router_status:
                        stat = router_status[p_key]
                        if stat['active']:
                            c_col3.success("Online")
                        else:
                            mins_left = int((stat['until'] - time.time()) / 60)
                            c_col3.error(f"Blacklisted ({mins_left}m)")
                    else:
                        c_col3.caption("Unknown")

                    if c_col4.button("🗑️", key=f"del_cand_{i}"):
                        candidates.pop(i)
                        update_config('llm', 'router', {'candidates': candidates, 'strategy': config.get('llm', {}).get('router', {}).get('strategy', 'priority')})
                        st.rerun()
            
            col_test, col_reset = st.columns(2)
            if col_test.button("🔌 Test All Connectivity", width="stretch"):
                 if hasattr(router, 'run_health_check'):
                    with st.spinner("Checking health of all models..."):
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(router.run_health_check())
                        st.success("Connectivity test complete!")
                        st.rerun()

            if col_reset.button("🔄 Reset Blacklist", width="stretch"):
                if hasattr(router, '_blacklist'):
                    router._blacklist.clear()
                    st.success("Blacklist cleared! All models will be retried.")
                    st.rerun()
            
            st.divider()
            
            # Discovery Tool
            st.markdown("#### 🔭 Model Discovery")
            if st.button("🚀 Scan for Free Models", type="primary", width="stretch"):
                with st.status("Scanning all configured providers for available free models...", expanded=True) as status:
                    def log_status(msg):
                        status.write(f"  {msg}")
                    
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        results = loop.run_until_complete(scan_all_free_providers(status_callback=log_status))
                        
                        if results:
                            st.session_state['discovered_models'] = results
                            status.update(label=f"Scan Complete! Found {len(results)} active models.", state="complete")
                        else:
                            st.error("No free models found. Check your API keys.")
                    except Exception as e:
                        st.error(f"Scan failed: {e}")
                
            if 'discovered_models' in st.session_state:
                st.markdown("##### Discovered Models")
                discovered = st.session_state['discovered_models']
                
                # Selection for adding
                to_add = st.multiselect("Select models to add to router candidates:", 
                                        [f"{m['provider']}/{m['model_name']}" for m in discovered],
                                        default=[f"{m['provider']}/{m['model_name']}" for m in discovered[:5]])
                
                if st.button("➕ Add Selected to Router"):
                    current_candidates = config.get('llm', {}).get('router', {}).get('candidates', [])
                    added_count = 0
                    for m_str in to_add:
                        p, m = m_str.split('/', 1)
                        # Avoid duplicates
                        if not any(c['provider'] == p and c['model_name'] == m for c in current_candidates):
                            current_candidates.append({'provider': p, 'model_name': m})
                            added_count += 1
                    
                    update_config('llm', 'router', {'candidates': current_candidates, 'strategy': 'priority'})
                    st.success(f"Added {added_count} candidates to router!")
                    del st.session_state['discovered_models']
                    st.rerun()
            
            if st.button("Save Router Mode"):
                update_config('llm', 'mode', 'router')
                st.success("Switched to Router Mode!")
                st.rerun()

    with settings_tab4:
        st.markdown("### Email Routing")
        
        current_email_provider = config.get('email', {}).get('provider', 'smtp')
        # All available "Type" options
        email_providers = ['smart', 'resend', 'brevo', 'sendgrid', 'mailjet', 'mailgun', 'postmark', 'mailersend', 'sendpulse', 'amazon_ses', 'mailtrap', 'zoho', 'netcore', 'smtp']
        
        new_email_provider = st.selectbox("Active Email Service", email_providers, index=email_providers.index(current_email_provider) if current_email_provider in email_providers else 0)
        
        if new_email_provider == 'smart':
            st.info("🧠 **Smart Router Active**: Emails will be routed based on the priority list below.")
            
            # --- Strategy Presets ---
            st.markdown("**Core Strategy Presets**")
            col_p1, col_p2, col_p3 = st.columns(3)
            
            preset_max_volume = ['sendpulse', 'brevo', 'mailjet', 'netcore', 'smtp2go', 'sendgrid', 'mailgun']
            preset_deliverability = ['postmark', 'amazon_ses', 'mailgun', 'zoho', 'resend', 'mailersend']
            preset_testing = ['mailtrap', 'mailersend'] 
            
            def apply_preset(name, providers):
                with open(config_path, 'r') as f: full_config = yaml.safe_load(f) or {}
                if 'email' not in full_config: full_config['email'] = {}
                if 'smart_routing' not in full_config['email']: full_config['email']['smart_routing'] = {}
                full_config['email']['smart_routing']['providers'] = providers
                with open(config_path, 'w') as f: yaml.dump(full_config, f, sort_keys=False)
                reload_config()
                st.toast(f"Applied {name} Preset!")
                time.sleep(1)
                st.rerun()

            if col_p1.button("🚀 Max Volume", width="stretch"):
                apply_preset("Max Volume", preset_max_volume)

            if col_p2.button("🛡️ High Deliverability", width="stretch"):
                apply_preset("High Deliverability", preset_deliverability)

            if col_p3.button("🧪 Sandbox / Testing", width="stretch"):
                 apply_preset("Testing", preset_testing)

            # --- Router Priority List (Drag & Drop) ---
            
            current_router_list = config.get('email', {}).get('smart_routing', {}).get('providers', [])
            if not current_router_list:
                current_router_list = ['mailjet', 'brevo', 'sendgrid', 'resend', 'mailgun', 'postmark', 'mailersend', 'sendpulse', 'amazon_ses', 'mailtrap', 'zoho', 'netcore']
            
            # Collect all possible providers (built-in + customs)
            builtins = ['mailjet', 'brevo', 'sendgrid', 'resend', 'mailgun', 'postmark', 'mailersend', 'sendpulse', 'amazon_ses', 'mailtrap', 'zoho', 'netcore', 'smtp']
            
            # Add custom names
            custom_configs = config.get('email', {}).get('custom_providers', [])
            custom_names = [f"custom_{c['name']}" for c in custom_configs if 'name' in c]
            
            available_providers = list(set(builtins + custom_names + current_router_list))
            
            selected_router_providers = st.multiselect(
                "Router Priority (Drag to Reorder)", 
                available_providers, 
                default=[p for p in current_router_list if p in available_providers],
                help="Emails will be attempted in this order. If one fails, the next is tried."
            )
            
            if st.button("Update Router Priority"):
                with open(config_path, 'r') as f:
                    full_config = yaml.safe_load(f) or {}
                
                if 'email' not in full_config: full_config['email'] = {}
                if 'smart_routing' not in full_config['email']: full_config['email']['smart_routing'] = {}
                
                full_config['email']['smart_routing']['providers'] = selected_router_providers
                
                with open(config_path, 'w') as f:
                    yaml.dump(full_config, f, sort_keys=False)
                
                reload_config()
                st.success("Router Priority Updated!")
                time.sleep(1)
                st.rerun()
                
            # --- Custom SMTP Form ---
            st.divider()
            with st.expander("➕ Add Custom SMTP Provider"):
                st.write("Add any other provider (e.g. Outlook, Yahoo, or your own server).")
                c_name = st.text_input("Provider Name (e.g. 'Office365')")
                c_host = st.text_input("SMTP Host")
                c_port = st.number_input("SMTP Port", value=587)
                c_user = st.text_input("Username")
                c_pass = st.text_input("Password", type="password")
                
                if st.button("Save Custom Provider"):
                    if c_name and c_host and c_user and c_pass:
                        with open(config_path, 'r') as f: full_config = yaml.safe_load(f) or {}
                        
                        if 'email' not in full_config: full_config['email'] = {}
                        if 'custom_providers' not in full_config['email']: full_config['email']['custom_providers'] = []
                        
                        # Check exist (update if same name)
                        exists = False
                        for i, p in enumerate(full_config['email']['custom_providers']):
                            if p.get('name') == c_name:
                                full_config['email']['custom_providers'][i] = {
                                    "name": c_name, "host": c_host, "port": c_port, "username": c_user, "password": c_pass
                                }
                                exists = True
                                break
                        
                        if not exists:
                            full_config['email']['custom_providers'].append({
                                    "name": c_name, "host": c_host, "port": c_port, "username": c_user, "password": c_pass
                            })
                            
                        with open(config_path, 'w') as f: yaml.dump(full_config, f, sort_keys=False)
                        reload_config()
                        st.success(f"Custom Provider '{c_name}' Saved! Add it to the priority list above.")
                        st.rerun()
                    else:
                        st.error("Please fill all fields.")

        st.divider()

        if st.button("Update Active Provider"):
                update_config('email', 'provider', new_email_provider)
                st.success(f"Email Provider switched to {new_email_provider}!")
                time.sleep(1)
                st.rerun()
    
    # Page level chat
    render_page_chat("System Admin", ManagerAgent(), "Ask about configuration or environment variables.")
