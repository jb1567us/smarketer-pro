import requests

def disable_injector():
    url = "https://elliotspencermorgan.com/safe_writer.php"
    remote_path = "wp-content/mu-plugins/esm-logo-injector.php"
    
    # Overwrite with empty/commented file
    content = "<?php\n// Plugin disabled by Antigravity\n?>"
    
    data = {
        'path': remote_path,
        'content': content
    }
    
    print(f"Disabling {remote_path}...")
    try:
        response = requests.post(url, data=data, verify=False, timeout=30)
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    disable_injector()
