import requests
import json

def deploy_json():
    url = "https://elliotspencermorgan.com/safe_writer.php"
    local_path = r"c:\sandbox\esm\artwork_data.json"
    remote_path = "artwork_data.json" # Root relative
    
    print(f"Reading {local_path}...")
    with open(local_path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Validation: Ensure JSON is valid before pushing
    try:
        json.loads(content)
        print("JSON validity check passed.")
    except json.JSONDecodeError as e:
        print(f"CRITICAL: JSON is invalid! Aborting deploy. {e}")
        return

    data = {
        'path': remote_path,
        'content': content
    }
    
    print(f"Deploying to {remote_path}...")
    try:
        response = requests.post(url, data=data, verify=False, timeout=30)
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    deploy_json()
