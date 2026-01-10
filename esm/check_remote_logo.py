import requests

logo_url = 'https://elliotspencermorgan.com/logo.png'
try:
    response = requests.head(logo_url, verify=False, timeout=10)
    if response.status_code == 200:
        print(f"Logo exists at {logo_url}")
    else:
        print(f"Logo NOT found at {logo_url} (Status: {response.status_code})")
except Exception as e:
    print(f"Error checking logo: {e}")
