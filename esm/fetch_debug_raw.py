import requests

def check_debug():
    url = "https://elliotspencermorgan.com/debug_server_file.php"
    try:
        response = requests.get(url, verify=False, timeout=10)
        print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    check_debug()
