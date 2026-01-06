import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def push_file(local, remote):
    url = "https://elliotspencermorgan.com/safe_writer.php"
    try:
        with open(local, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading local file: {e}")
        return

    data = {
        'path': remote,
        'content': content
    }
    
    print(f"Pushing {local} to {remote} via {url}...")
    try:
        response = requests.post(url, data=data, verify=False, timeout=30)
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    push_file(r"c:\sandbox\esm\artwork_data.json", "wp-content/plugins/artwork_data.json")
