import os
from dotenv import load_dotenv

# Load environment variables from main app's .env if not already handled
load_dotenv()

class HostingConfig:
    def __init__(self):
        self.data = self._load_from_env()

    def _load_from_env(self):
        config = {}
        # Environment variables direct mapping
        config["cpanel_url"] = os.getenv("CPANEL_URL", "")
        config["cpanel_user"] = os.getenv("CPANEL_USER", "")
        config["cpanel_token"] = os.getenv("CPANEL_TOKEN", "")
        config["cpanel_password"] = os.getenv("CPANEL_PASSWORD", "")
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
        if not self.cpanel_url or not self.cpanel_user:
             raise ValueError("Missing CPANEL_URL or CPANEL_USER in .env")
             
        if not self.cpanel_token and not self.cpanel_password:
             raise ValueError("Missing authentication: Set CPANEL_TOKEN or CPANEL_PASSWORD in .env")
