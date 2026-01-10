import requests
import urllib3
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def push_file(local_path, remote_path_rel):
    url = "https://elliotspencermorgan.com/safe_writer.php"
    
    if not os.path.exists(local_path):
        print(f"Error: Local file not found: {local_path}")
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
        print(f"Response: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Deploy PHP
    push_file(r"c:\sandbox\esm\esm-trade-portal.php", "content/plugins/esm-trade-portal/esm-trade-portal.php")
    
    # Deploy JS
    push_file(r"c:\sandbox\esm\esm-trade-portal.js", "content/plugins/esm-trade-portal/esm-trade-portal.js")
