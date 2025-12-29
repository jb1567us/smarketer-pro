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
