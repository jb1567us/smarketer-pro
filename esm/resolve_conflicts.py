import requests

# disable warning
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def resolve():
    url = "https://elliotspencermorgan.com/safe_writer.php"
    
    paths = [
        'wp-content/mu-plugins/esm-artwork-template.php',
        'wp-content/plugins/esm-artwork-template/esm-artwork-template.php',
        'wp-content/plugins/esm-artwork-template.php',
        'wp-content/plugins/esm-deployment-fix.php.bak',
        'wp-content/plugins/esm-template-v3.php',
        'wp-content/plugins/esm-trade-portal.php.bak',
        'wp-content/mu-plugins/esm-artwork-template_NEW.php.bak',
        'wp-content/mu-plugins/esm-deployment-fix.php.bak'
    ]
    
    for p in paths:
        data = {
            'action': 'delete',
            'path': p
        }
        print(f"Deleting {p}...")
        r = requests.post(url, data=data, verify=False)
        print(r.text)

if __name__ == "__main__":
    resolve()

if __name__ == "__main__":
    resolve()
