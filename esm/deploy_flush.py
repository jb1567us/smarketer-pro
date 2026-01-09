
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def deploy_flush():
    url = "https://elliotspencermorgan.com/safe_writer.php"
    local = r"c:\sandbox\esm\flush_cache.php"
    
    with open(local, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("Pushing flush_cache.php...")
    r = requests.post(url, data={'path': 'flush_cache.php', 'content': content}, verify=False)
    print(f"Response: {r.text}")

if __name__ == "__main__":
    deploy_flush()
