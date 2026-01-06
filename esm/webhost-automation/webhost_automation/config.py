import os
import yaml
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.data = self._load_config()

    def _load_config(self):
        config = {}
        # Load from YAML if exists
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as f:
                config = yaml.safe_load(f) or {}
        
        # Environment variables override config file
        if os.getenv("CPANEL_URL"):
            config["cpanel_url"] = os.getenv("CPANEL_URL")
        if os.getenv("CPANEL_USER"):
            config["cpanel_user"] = os.getenv("CPANEL_USER")
        if os.getenv("CPANEL_TOKEN"):
            config["cpanel_token"] = os.getenv("CPANEL_TOKEN")
        if os.getenv("CPANEL_PASSWORD"):
            config["cpanel_password"] = os.getenv("CPANEL_PASSWORD")
            
        return config

    @property
    def cpanel_url(self):
        return self.data.get("cpanel_url", "").rstrip("/")

    @property
    def cpanel_user(self):
        return self.data.get("cpanel_user", "")

    @property
    def cpanel_token(self):
        return self.data.get("cpanel_token", "")

    @property
    def cpanel_password(self):
        return self.data.get("cpanel_password", "")

    def validate(self):
        # We need URL and User at minimum
        if not self.cpanel_url or not self.cpanel_user:
             raise ValueError("Missing CPANEL_URL or CPANEL_USER")
             
        # For auth, we need either Token OR Password
        if not self.cpanel_token and not self.cpanel_password:
             raise ValueError("Missing authentication: Provide CPANEL_TOKEN (for API) or CPANEL_PASSWORD (for Browser)")
