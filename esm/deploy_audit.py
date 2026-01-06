
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def deploy_audit():
    url = "https://elliotspencermorgan.com/safe_writer.php"
    local = r"c:\sandbox\esm\audit_plugins.php"
    
    with open(local, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("Pushing audit_plugins.php...")
    r = requests.post(url, data={'path': 'audit_plugins.php', 'content': content}, verify=False)
    print(f"Response: {r.text}")

if __name__ == "__main__":
    deploy_audit()
