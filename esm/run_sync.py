import requests

def run_sync():
    url = "https://elliotspencermorgan.com/sync_json_to_db.php"
    headers = {'User-Agent': 'Mozilla/5.0'}
    print(f"Executing {url}...")
    try:
        r = requests.get(url, headers=headers, verify=False, timeout=60)
        print(f"Status: {r.status_code}")
        print(r.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    run_sync()
