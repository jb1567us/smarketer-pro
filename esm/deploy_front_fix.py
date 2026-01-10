import requests

def deploy_front_fix():
    url = "https://elliotspencermorgan.com/safe_writer.php"
    local_path = r"c:\sandbox\esm\wp-content\themes\caviar-premium\front-page.php"
    remote_path = "wp-content/themes/caviar-premium/front-page.php"
    
    with open(local_path, 'r', encoding='utf-8') as f:
        content = f.read()
            
    data = {
        'path': remote_path,
        'content': content
    }
    
    print(f"Deploying {local_path}...")
    try:
        response = requests.post(url, data=data, verify=False, timeout=30)
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    deploy_front_fix()
