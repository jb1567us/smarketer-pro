import requests
import time

def check_searxng():
    url = "http://localhost:8080/"
    # params = {"q": "test", "format": "json"}
    
    print("Checking SearXNG at http://localhost:8080...")
    for i in range(10):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print("SearXNG is UP and returning results!")
                print(f"Sample Result Title: {response.json().get('results', [{}])[0].get('title', 'No title')}")
                return
            else:
                print(f"Status Code: {response.status_code}. Retrying...")
        except Exception as e:
            print(f"Connection failed: {e}. Retrying ({i+1}/10)...")
        
        time.sleep(2)

    print("Failed to connect to SearXNG after retries.")

if __name__ == "__main__":
    check_searxng()
