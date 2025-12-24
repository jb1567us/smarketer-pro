import requests
import sys

def check_url(url):
    try:
        print(f"Checking {url}...")
        response = requests.get(url, verify=False, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Content Preview: {response.text[:200]}")
        if response.status_code == 200 and "Deployment" in response.text:
            print("SUCCESS: Script found!")
            return True
        else:
            print("FAILURE: Script not found or error.")
            return False
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    check_url("https://elliotspencermorgan.com/deploy_core_fix.php")
