import sys
sys.path.append('src')
from model_fetcher import scan_all_free_providers
import yaml
from config import config

print("Scanning for free models...")
candidates = scan_all_free_providers()
print(f'Found {len(candidates)} models')

if candidates:
    # Ensure nested keys exist
    if 'llm' not in config: config['llm'] = {}
    if 'router' not in config['llm']: config['llm']['router'] = {}
    
    config['llm']['router']['candidates'] = candidates
    config['llm']['mode'] = 'router'
    
    with open('config.yaml', 'w') as f:
        yaml.dump(config, f, sort_keys=False)
    print("config.yaml updated.")
else:
    print("No models found.")
