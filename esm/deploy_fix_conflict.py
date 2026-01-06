
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def deploy_fix():
    url = "https://elliotspencermorgan.com/safe_writer.php"
    local = r"c:\sandbox\esm\fix_mu_conflict.php"
    
    with open(local, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("Pushing fix_mu_conflict.php...")
    r = requests.post(url, data={'path': 'fix_mu_conflict.php', 'content': content}, verify=False)
    print(f"Response: {r.text}")

if __name__ == "__main__":
    deploy_fix()
