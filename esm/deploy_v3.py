
import requests
import urllib3
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def deploy_v3():
    url = "https://elliotspencermorgan.com/safe_writer.php"
    
    # Files to deploy
    # Note: We deploy to both wp-content and content just to be sure, 
    # though we know wp-content/plugins is the active one now after the conflict fix.
    
    files = [
        (r"c:\sandbox\esm\esm-trade-portal-v3.js", "wp-content/plugins/esm-trade-portal/esm-trade-portal-v3.js"),
        (r"c:\sandbox\esm\esm-trade-portal-v3.js", "content/plugins/esm-trade-portal/esm-trade-portal-v3.js"),
        (r"c:\sandbox\esm\esm-trade-portal-v3.php", "wp-content/plugins/esm-trade-portal/esm-trade-portal.php"),
        (r"c:\sandbox\esm\esm-trade-portal-v3.php", "content/plugins/esm-trade-portal/esm-trade-portal.php"),
    ]
    
    for local, remote in files:
        print(f"Pushing {local} -> {remote}")
        with open(local, 'r', encoding='utf-8') as f:
            content = f.read()
        
        r = requests.post(url, data={'path': remote, 'content': content}, verify=False)
        print(f"Response: {r.text}")
        time.sleep(0.5)

    # Flush Cache logic re-use? or just rely on opcache reset in safe_writer?
    # safe_writer resets opcache.
    # W3TC/etc might need manual flush.
    
    print("Triggering flush_cache.php...")
    try:
        requests.get("https://elliotspencermorgan.com/flush_cache.php", verify=False, timeout=10)
    except:
        pass
    print("Done.")

if __name__ == "__main__":
    deploy_v3()
