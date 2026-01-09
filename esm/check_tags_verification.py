import requests
import base64

WP_URL = "https://elliotspencermorgan.com"
WP_USER = "admin"
WP_APP_PASSWORD = "YHKK gZpc xCpt aNJs UPQe ABcg"

def main():
    api_url = f"{WP_URL}/wp-json/wp/v2"
    credentials = f"{WP_USER}:{WP_APP_PASSWORD}"
    token = base64.b64encode(credentials.encode()).decode('utf-8')
    headers = {'Authorization': f'Basic {token}'}

    # Get latest modified page
    print("Fetching latest modified page...")
    resp = requests.get(f"{api_url}/pages?per_page=1&orderby=modified&order=desc", headers=headers)
    
    if resp.status_code == 200:
        pages = resp.json()
        if pages:
            p = pages[0]
            print(f"Latest Page: {p['title']['rendered']} (ID: {p['id']})")
            print(f"Tags Count: {len(p['tags'])}")
            print(f"Tag IDs: {p['tags']}")
            
            # Fetch details for these tags
            if p['tags']:
                print("Resolving tag names...")
                tag_names = []
                for t_id in p['tags']:
                    t_resp = requests.get(f"{api_url}/tags/{t_id}", headers=headers)
                    if t_resp.status_code == 200:
                        tag_names.append(t_resp.json()['name'])
                print(f"Tags: {', '.join(tag_names)}")
            else:
                print("❌ No tags found on this page.")
        else:
            print("No pages found.")
    else:
        print(f"Error: {resp.status_code}")

if __name__ == "__main__":
    main()
