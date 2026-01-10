
import requests
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def push_probe():
    url = "https://elliotspencermorgan.com/safe_writer.php"
    local_path = r"c:\sandbox\esm\probe_deploy.php"
    
    with open(local_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    data = {
        'path': 'probe_deploy.php',
        'content': content
    }
    
    print(f"Pushing probe to root...")
    try:
        response = requests.post(url, data=data, verify=False, timeout=30)
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error pushing file: {e}")

if __name__ == "__main__":
    push_probe()
