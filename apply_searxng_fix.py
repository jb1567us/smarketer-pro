import yaml
import os

SETTINGS_PATH = r"c:\sandbox\b2b_outreach_tool\searxng\searxng\settings.yml"

def apply_fix():
    if not os.path.exists(SETTINGS_PATH):
        print(f"File not found: {SETTINGS_PATH}")
        return

    print("Reading settings.yml...")
    with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
        try:
            # parsing huge file might be slow
            data = yaml.safe_load(f)
        except Exception as e:
            print(f"Error parsing YAML: {e}")
            # Fallback for simple line processing if yaml fails
            return

    if 'outgoing' not in data:
        data['outgoing'] = {}
    
    # Increase timeout
    print("Setting outgoing request_timeout to 20.0...")
    data['outgoing']['request_timeout'] = 20.0
    data['outgoing']['max_request_timeout'] = 20.0
    
    # Clear proxies
    if 'proxies' in data['outgoing']:
        print(f"Removing {len(data['outgoing']['proxies'].get('all://', []))} proxies specific to 'all://'...")
        # We keep the structure but empty the list to use direct connection/Tor
        data['outgoing']['proxies'] = {'all://': []}
        
    print("Writing settings.yml...")
    with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False)
    
    print("Success! Settings updated.")

if __name__ == "__main__":
    apply_fix()
