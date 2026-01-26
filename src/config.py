import yaml
import os
import sys
from utils.secrets import secrets

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.yaml")

def load_config():
    """Loads the YAML configuration file."""
    if not os.path.exists(CONFIG_PATH):
        print(f"Error: Config file not found at {CONFIG_PATH}")
        sys.exit(1)
        
    with open(CONFIG_PATH, "r") as f:
        try:
            config = yaml.safe_load(f)
            return config
        except yaml.YAMLError as exc:
            print(f"Error parsing config.yaml: {exc}")
            sys.exit(1)

# Global config object
config = load_config()

def reload_config():
    """Reloads the configuration from the YAML file."""
    global config
    config.clear()
    config.update(load_config())
    _inject_env_config()

def _inject_env_config():
    """Injects environment variables into the config dictionary."""
    if 'ftp' not in config:
        config['ftp'] = {}
    
    # FTP Overrides from Env (Safe Get)
    if secrets.get('FTP_HOST'): config['ftp']['host'] = secrets.get('FTP_HOST')
    if secrets.get('FTP_USER'): config['ftp']['user'] = secrets.get('FTP_USER')
    if secrets.get('FTP_PASS'): config['ftp']['pass'] = secrets.get('FTP_PASS')
    if secrets.get('FTP_PORT'): config['ftp']['port'] = secrets.get('FTP_PORT')

# Initial injection
_inject_env_config()

def get_smtp_config():
    """Helper to resolve environment variables in SMTP config."""
    c = config.get("email", {})
    user = c.get("smtp_user", "")
    password = c.get("smtp_pass", "")
    
    # Simple env var substitution if they start with $
    if user.startswith("${") and user.endswith("}"):
        var_name = user[2:-1]
        user = secrets.get(var_name, "")
        
    if password.startswith("${") and password.endswith("}"):
        var_name = password[2:-1]
        password = secrets.get(var_name, "")
        
    return c["smtp_server"], c["smtp_port"], user, password

def update_config(section, key, value):
    """Updates config.yaml and reloads."""
    with open(CONFIG_PATH, 'r') as f:
        full_config = yaml.safe_load(f) or {}
        
    if section not in full_config:
        full_config[section] = {}
        
    full_config[section][key] = value
    
    with open(CONFIG_PATH, 'w') as f:
        yaml.dump(full_config, f, sort_keys=False)
        
    reload_config()

def get_cpanel_config():
    """Returns cPanel configuration from environment or config."""
    cp = config.get("cpanel", {})
    url = secrets.get("CPANEL_URL") or cp.get("url", "")
    user = secrets.get("CPANEL_USER") or cp.get("user", "")
    token = secrets.get("CPANEL_TOKEN") or secrets.get("CPANEL_PASS") or cp.get("token", "")
    domain = secrets.get("CPANEL_DOMAIN") or cp.get("domain", "")
    
    return {
        "url": url,
        "user": user,
        "token": token,
        "domain": domain
    }
