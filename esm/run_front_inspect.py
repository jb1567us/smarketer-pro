import requests

def run_front_inspect():
    url = "https://elliotspencermorgan.com/inspect_front_page.php"
    headers = {'User-Agent': 'Mozilla/5.0'}
    print(f"Executing {url}...")
    try:
        r = requests.get(url, headers=headers, verify=False, timeout=30)
        print(r.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    run_front_inspect()
