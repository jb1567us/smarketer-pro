import streamlit as st
import os
import yaml
import time
from config import config, reload_config

def render_settings_page():
    st.header("⚙️ Configuration")
    
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config.yaml')

    # Helper to update .env
    def update_env(key, value):
        # Read current .env
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

    with settings_tab2:
        st.subheader("API Key Management")
        st.info("Keys are stored in your local `.env` file.")
        
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
            col1, col2 = st.columns([3, 1])
            with col1:
                current_val = os.getenv(key, "")
                new_val = st.text_input(f"{key}", value=current_val, type="password")
                if new_val != current_val:
                    update_env(key, new_val)
                    st.toast(f"Updated {key}")
            with col2:
                if key in key_links:
                    st.markdown(f"[Get Key]({key_links[key]})")
        
        st.divider()
        st.markdown("#### 🧠 AI Models")
        llm_keys = [
            "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", 
            "OPENROUTER_API_KEY", "GROQ_API_KEY", "MISTRAL_API_KEY",
            "HUGGINGFACE_API_KEY", "GITHUB_TOKEN", "CEREBRAS_API_KEY",
            "NVIDIA_API_KEY", "COHERE_API_KEY", "CLOUDFLARE_ACCOUNT_ID", "CLOUDFLARE_API_KEY"
        ]
        for key in llm_keys:
            col1, col2 = st.columns([3, 1])
            with col1:
                current_val = os.getenv(key, "")
                new_val = st.text_input(f"{key}", value=current_val, type="password")
                if new_val != current_val:
                    update_env(key, new_val)
                    st.toast(f"Updated {key}")
            with col2:
                if key in key_links:
                     st.markdown(f"[Get Key]({key_links[key]})")

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
            
            # Preset Maps
            preset_max_volume = ['sendpulse', 'brevo', 'mailjet', 'netcore', 'smtp2go', 'sendgrid', 'mailgun']
            preset_deliverability = ['postmark', 'amazon_ses', 'mailgun', 'zoho', 'resend', 'mailersend']
            preset_testing = ['mailtrap', 'mailersend'] 
            
            if col_p1.button("🚀 Max Volume"):
                # Apply Max Volume Preset
                with open(config_path, 'r') as f: full_config = yaml.safe_load(f) or {}
                if 'email' not in full_config: full_config['email'] = {}
                if 'smart_routing' not in full_config['email']: full_config['email']['smart_routing'] = {}
                full_config['email']['smart_routing']['providers'] = preset_max_volume
                with open(config_path, 'w') as f: yaml.dump(full_config, f, sort_keys=False)
                reload_config()
                st.rerun()

            if col_p2.button("🛡️ High Deliverability"):
                # Apply Deliverability Preset
                with open(config_path, 'r') as f: full_config = yaml.safe_load(f) or {}
                if 'email' not in full_config: full_config['email'] = {}
                if 'smart_routing' not in full_config['email']: full_config['email']['smart_routing'] = {}
                full_config['email']['smart_routing']['providers'] = preset_deliverability
                with open(config_path, 'w') as f: yaml.dump(full_config, f, sort_keys=False)
                reload_config()
                st.rerun()

            if col_p3.button("🧪 Sandbox / Testing"):
                 # Apply Testing Preset
                with open(config_path, 'r') as f: full_config = yaml.safe_load(f) or {}
                if 'email' not in full_config: full_config['email'] = {}
                if 'smart_routing' not in full_config['email']: full_config['email']['smart_routing'] = {}
                full_config['email']['smart_routing']['providers'] = preset_testing
                with open(config_path, 'w') as f: yaml.dump(full_config, f, sort_keys=False)
                reload_config()
                st.rerun()

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
                            
                        # Also auto-add to smart routing list?
                        # Let's direct user to add it manually to keep logic safe
                        
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

