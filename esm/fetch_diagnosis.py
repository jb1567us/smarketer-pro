import requests
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch():
    url = "https://elliotspencermorgan.com/diagnose_server.php"
    try:
        print(f"Fetching {url}...")
        r = requests.get(url, verify=False, timeout=30)
        with open("diagnosis.html", "w", encoding='utf-8') as f:
            f.write(r.text)
        print("Wrote to diagnosis.html")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch()
