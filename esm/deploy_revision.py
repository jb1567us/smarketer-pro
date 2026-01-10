
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def deploy_revision_strategy():
    url = "https://elliotspencermorgan.com/safe_writer.php"
    
    # 1. PUSH JS as NEW file name
    js_local = r"c:\sandbox\esm\esm-trade-portal.js"
    with open(js_local, 'r', encoding='utf-8') as f:
        js_content = f.read()

    # Target path: wp-content/plugins/esm-trade-portal/esm-trade-portal-v2.js
    # AND content/plugins/... just in case
    print("Pushing NEW JS file (esm-trade-portal-v2.js)...")
    
    targets_js = [
        "wp-content/plugins/esm-trade-portal/esm-trade-portal-v2.js",
        "content/plugins/esm-trade-portal/esm-trade-portal-v2.js"
    ]
    
    for t in targets_js:
        r = requests.post(url, data={'path': t, 'content': js_content}, verify=False)
        print(f"[{t}] Response: {r.text}")

    # 2. PUSH PHP (Updated to load v2.js)
    php_local = r"c:\sandbox\esm\esm-trade-portal.php"
    with open(php_local, 'r', encoding='utf-8') as f:
        php_content = f.read()
        
    targets_php = [
        "wp-content/plugins/esm-trade-portal/esm-trade-portal.php",
        "content/plugins/esm-trade-portal/esm-trade-portal.php"
    ]
    
    print("Pushing updated PHP file...")
    for t in targets_php:
        r = requests.post(url, data={'path': t, 'content': php_content}, verify=False)
        print(f"[{t}] Response: {r.text}")

if __name__ == "__main__":
    deploy_revision_strategy()
