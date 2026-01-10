
import requests
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def push_file(local_path, remote_path_rel):
    url = "https://elliotspencermorgan.com/safe_writer.php"
    
    if not os.path.exists(local_path):
        print(f"ERROR: Local file not found: {local_path}")
        return

    with open(local_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    data = {
        'path': remote_path_rel,
        'content': content
    }
    
    print(f"Pushing {local_path} to {remote_path_rel}...")
    try:
        response = requests.post(url, data=data, verify=False, timeout=30)
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error pushing file: {e}")

if __name__ == "__main__":
    # Deploy PHP
    push_file(r"c:\sandbox\esm\esm-trade-portal.php", "wp-content/plugins/esm-trade-portal/esm-trade-portal.php")
    
    # Deploy JS
    push_file(r"c:\sandbox\esm\esm-trade-portal.js", "wp-content/plugins/esm-trade-portal/esm-trade-portal.js")
