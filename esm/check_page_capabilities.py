import requests
import base64
import json

WP_URL = "https://elliotspencermorgan.com"
WP_USER = "admin"
WP_APP_PASSWORD = "YHKK gZpc xCpt aNJs UPQe ABcg"

def main():
    api_url = f"{WP_URL}/wp-json/wp/v2"
    credentials = f"{WP_USER}:{WP_APP_PASSWORD}"
    token = base64.b64encode(credentials.encode()).decode('utf-8')
    headers = {'Authorization': f'Basic {token}'}

    print("Checking 'page' type capabilities...")
    resp = requests.get(f"{api_url}/types/page", headers=headers)
    
    if resp.status_code == 200:
        data = resp.json()
        print(json.dumps(data, indent=2))
        if 'taxonomies' in data:
            print(f"\nSupported Taxonomies: {data['taxonomies']}")
            if 'post_tag' in data['taxonomies']:
                print("✅ Pages SUPPORT tags.")
            else:
                print("❌ Pages DO NOT support tags (post_tag).")
        else:
            print("Could not find taxonomies field.")
    else:
        print(f"Error: {resp.status_code}")

if __name__ == "__main__":
    main()
