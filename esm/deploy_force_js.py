
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def deploy_force_js():
    url = "https://elliotspencermorgan.com/safe_writer.php"
    
    # 1. DELETE JS
    print("Deleting JS file...")
    requests.post(url, data={'action': 'delete', 'path': 'wp-content/plugins/esm-trade-portal/esm-trade-portal.js'}, verify=False)
    requests.post(url, data={'action': 'delete', 'path': 'content/plugins/esm-trade-portal/esm-trade-portal.js'}, verify=False)

    # 2. PUSH JS
    local_path = r"c:\sandbox\esm\esm-trade-portal.js"
    with open(local_path, 'r', encoding='utf-8') as f:
        content = f.read()

    print("Pushing JS file to wp-content...")
    r1 = requests.post(url, data={'path': 'wp-content/plugins/esm-trade-portal/esm-trade-portal.js', 'content': content}, verify=False)
    print(f"WP-Content Response: {r1.text}")

    print("Pushing JS file to content/...")
    r2 = requests.post(url, data={'path': 'content/plugins/esm-trade-portal/esm-trade-portal.js', 'content': content}, verify=False)
    print(f"Content Response: {r2.text}")
    
    # 3. PUSH Probe (Update)
    with open(r"c:\sandbox\esm\probe_deploy.php", 'r', encoding='utf-8') as f:
        probe_content = f.read()
    requests.post(url, data={'path': 'probe_deploy.php', 'content': probe_content}, verify=False)

if __name__ == "__main__":
    deploy_force_js()
