
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def deploy_debug():
    url = "https://elliotspencermorgan.com/safe_writer.php"
    local = r"c:\sandbox\esm\esm-trade-portal.php"
    
    with open(local, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("Pushing DEBUG PHP to both locations...")
    paths = [
        "wp-content/plugins/esm-trade-portal/esm-trade-portal.php",
        "content/plugins/esm-trade-portal/esm-trade-portal.php"
    ]
    
    for p in paths:
        r = requests.post(url, data={'path': p, 'content': content}, verify=False)
        print(f"[{p}]: {r.text}")

if __name__ == "__main__":
    deploy_debug()
