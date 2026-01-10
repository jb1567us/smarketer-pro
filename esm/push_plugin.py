import requests
import os

# disable warning
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def push_file(local_path, remote_path_rel):
    url = "https://elliotspencermorgan.com/safe_writer.php"
    with open(local_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    data = {
        'path': remote_path_rel,
        'content': content
    }
    
    print(f"Pushing {local_path} to {remote_path_rel} via {url}...")
    response = requests.post(url, data=data, verify=False, timeout=30)
    print(f"Response: {response.text}")

if __name__ == "__main__":
    push_file(r"c:\sandbox\esm\diagnose_server.php", "diagnose_server.php")
