import os
import sys
from dotenv import load_dotenv

# Ensure singleton behavior
_initialized = False

class SecretManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SecretManager, cls).__new__(cls)
            cls._instance._init_once()
        return cls._instance

    def _init_once(self):
        global _initialized
        if _initialized: return
        
        # Load .env file
        # Look for .env in root or src parent
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        env_path = os.path.join(base_dir, ".env")
        
        if os.path.exists(env_path):
            load_dotenv(env_path, override=True)
            print(f"[SecretManager] Loaded environment from {env_path}")
        else:
            print("[SecretManager] ⚠️ .env file not found. Relying on system environment variables.")

        # Critical Keys to Validate
        self.critical_keys = [
            # "OPENAI_API_KEY", # Optional if using Ollama
            # "DATABASE_URL"    # Using SQLite default
        ]
        
        self.validate()
        _initialized = True

    def get(self, key, default=None):
        """Safe getter for secrets."""
        val = os.getenv(key, default)
        return val

    def require(self, key):
        """Strict getter that raises error if missing."""
        val = os.getenv(key)
        if not val:
            raise EnvironmentError(f"Missing required environment variable: {key}")
        return val

    def validate(self):
        """Checks for presence of critical keys."""
        missing = []
        for k in self.critical_keys:
            if not os.getenv(k):
                missing.append(k)
        
        if missing:
             # Just warn for now to avoid breaking existing setups that might use defaults
             print(f"[SecretManager] ⚠️ Missing recommended keys: {', '.join(missing)}")

# Global Instance
secrets = SecretManager()
