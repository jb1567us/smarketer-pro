import yaml
import os
import sys

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.yaml")
ENV_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")

def load_env():
    """Manually load .env file to avoid python-dotenv dependency."""
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    os.environ[key] = value

load_env()

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
    
    # FTP Overrides from Env
    if os.getenv('FTP_HOST'): config['ftp']['host'] = os.getenv('FTP_HOST')
    if os.getenv('FTP_USER'): config['ftp']['user'] = os.getenv('FTP_USER')
    if os.getenv('FTP_PASS'): config['ftp']['pass'] = os.getenv('FTP_PASS')
    if os.getenv('FTP_PORT'): config['ftp']['port'] = os.getenv('FTP_PORT')

    # SearXNG Config: Env > Auto-Fallback > Default
    if 'search' not in config:
        config['search'] = {}

    env_url = os.getenv('SEARXNG_URL')
    if env_url:
         config['search']['searxng_url'] = env_url
    elif "localhost" in config['search'].get('searxng_url', ''):
         # Auto-fallback for cloud deployments (avoid localhost)
         config['search']['searxng_url'] = "https://searx.be/search"

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
        user = os.getenv(var_name, "")
        
    if password.startswith("${") and password.endswith("}"):
        var_name = password[2:-1]
        password = os.getenv(var_name, "")
        
    return c["smtp_server"], c["smtp_port"], user, password

def get_cpanel_config():
    """Helper to get cPanel config."""
    c = config.get("cpanel", {})
    return {
        'url': os.getenv('CPANEL_URL', config.get('cpanel', {}).get('url')),
        'user': os.getenv('CPANEL_USER', config.get('cpanel', {}).get('user')),
        'token': os.getenv('CPANEL_TOKEN', config.get('cpanel', {}).get('token')),
        'domain': os.getenv('CPANEL_DOMAIN', config.get('cpanel', {}).get('domain'))
    }
