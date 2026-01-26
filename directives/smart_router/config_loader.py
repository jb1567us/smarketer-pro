import yaml
import os

class DirectiveConfig:
    _data = {}

    @classmethod
    def load(cls):
        # Look for router_config.yaml in the parent directory of this package (directives/)
        # Current file: directives/smart_router/config_loader.py
        # Config file: directives/router_config.yaml
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, 'router_config.yaml')
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    cls._data = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"[SmartRouter] Error loading config from {config_path}: {e}")
        else:
             print(f"[SmartRouter] Warning: Config not found at {config_path}")

    @classmethod
    def get(cls, key, default=None):
        if not cls._data:
            cls.load()
        return cls._data.get(key, default)
