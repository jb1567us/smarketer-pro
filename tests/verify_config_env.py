import os
import sys

# Mock Env Vars BEFORE importing config
os.environ['FTP_HOST'] = 'env-verified-host.com'
os.environ['FTP_USER'] = 'env-verified-user'

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from config import config, reload_config

# Reload to pick up the env vars we just set (since config is loaded on import)
reload_config()

print(f"FTP Host in Config: {config.get('ftp', {}).get('host')}")
print(f"FTP User in Config: {config.get('ftp', {}).get('user')}")

if config.get('ftp', {}).get('host') == 'env-verified-host.com':
    print("SUCCESS: Config loaded from Env")
else:
    print("FAILURE: Config did not load from Env")
