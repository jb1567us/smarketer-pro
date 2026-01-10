import requests
import json
import base64
import time
import sys
from urllib.parse import urljoin

# --- CONFIGURATION ---
WP_URL = "https://elliotspencermorgan.com"
WP_USER = "admin"
WP_APP_PASSWORD = "YHKK gZpc xCpt aNJs UPQe ABcg"  # Provided by user
DATA_FILE = "c:\\sandbox\\esm\\enhanced_artwork_data.json"
ORIGINAL_DATA_FILE = "c:\\sandbox\\esm\\artwork_data.json"

# --- SMART TAGS LOGIC ---
def generate_smart_tags(item, full_item_data):
    tags = set()
    
    # 1. Styles
    if item.get('styles'):
        for s in item['styles'].split(','):
            tags.add(s.strip())
            
    # 2. Mediums
    if item.get('mediumsDetailed'):
        for m in item['mediumsDetailed'].split(','):
            tags.add(m.strip())
    elif item.get('medium'):
        tags.add(item['medium'])
        
    # 3. Colors (from full data if available)
    if full_item_data and full_item_data.get('detected_colors'):
        for c in full_item_data['detected_colors']:
            tags.add(c)
        if len(full_item_data['detected_colors']) > 3:
            tags.add('Colorful')
        if len(full_item_data['detected_colors']) > 1:
            tags.add('Multicolored')

    # 4. Base Tags
    tags.add('Contemporary Art')
    tags.add('Fine Art')
    tags.add('Elliot Spencer Morgan')
    
    return list(tags)

# --- API CLIENT ---
class WordPressClient:
    def __init__(self, url, user, password):
        self.base_url = url.rstrip('/') + "/wp-json/wp/v2"
        self.auth = (user, password)
        self.tag_cache = {} # Name -> ID

    def get_headers(self):
        return {
            "Content-Type": "application/json"
        }

    def _request(self, method, endpoint, data=None, params=None):
        url = f"{self.base_url}/{endpoint}"
        try:
            if method == 'GET':
                resp = requests.get(url, auth=self.auth, headers=self.get_headers(), params=params)
            elif method == 'POST':
                resp = requests.post(url, auth=self.auth, headers=self.get_headers(), json=data)
            elif method == 'PUT':
                resp = requests.put(url, auth=self.auth, headers=self.get_headers(), json=data)
            
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.HTTPError as e:
            print(f"Error {method} {url}: {e}")
            if e.response is not None:
                print(f"Response: {e.response.text}")
            return None

    def get_all_tags(self):
        print("Fetching existing tags...")
        tags = []
        page = 1
        while True:
            batch = self._request('GET', 'tags', params={'per_page': 100, 'page': page})
            if not batch:
                break
            tags.extend(batch)
            if len(batch) < 100:
                break
            page += 1
        
        self.tag_cache = {t['name'].lower(): t['id'] for t in tags}
        print(f"Found {len(self.tag_cache)} existing tags.")

    def get_or_create_tag_id(self, tag_name):
        tag_key = tag_name.lower()
        if tag_key in self.tag_cache:
            return self.tag_cache[tag_key]
        
        # Create
        print(f"Creating tag: {tag_name}")
        data = {'name': tag_name}
        resp = self._request('POST', 'tags', data=data)
        if resp:
            new_id = resp['id']
            self.tag_cache[tag_key] = new_id
            return new_id
        return None

    def find_page_by_slug(self, slug):
        items = self._request('GET', 'pages', params={'slug': slug})
        if items and len(items) > 0:
            return items[0]
        return None

    def find_page_by_title(self, title):
        items = self._request('GET', 'pages', params={'search': title})
        if items:
            # Exact match check
            for item in items:
                if item['title']['rendered'] == title:
                    return item
        return None

    def update_page_tags(self, page_id, tag_ids):
        data = {'tags': tag_ids}
        resp = self._request('POST', f'pages/{page_id}', data=data)
        return resp is not None

# --- MAIN ---
def main():
    print("Starting Tag Update Script...")
    
    # 1. Load Data
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            enhanced_data = json.load(f)
        
        with open(ORIGINAL_DATA_FILE, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
            # Create a map for easy lookup
            original_map = {str(item['id']): item for item in original_data}
            
    except Exception as e:
        print(f"Error loading data: {e}")
        return

    # 2. Initialize Client
    client = WordPressClient(WP_URL, WP_USER, WP_APP_PASSWORD)
    
    # Check connection
    user = client._request('GET', 'users/me')
    if not user:
        print("Authentication failed. Check credentials.")
        return
    print(f"Authenticated as: {user['name']}")

    # 3. Pre-fetch Tags
    client.get_all_tags()

    # 4. Process Items
    success_count = 0
    fail_count = 0
    
    total = len(enhanced_data)
    for index, item in enumerate(enhanced_data):
        print(f"\nProcessing {index+1}/{total}: {item['title']}")
        
        # Get full data for deeper tag logic (colors)
        full_data = original_map.get(str(item['id']))
        if not full_data:
             # Try simpler lookup if ID mismatch or string/int issue
             full_data = next((x for x in original_data if x['title'] == item['title']), None)

        # Generate Tags
        tag_names = generate_smart_tags(item, full_data)
        print(f"  Generated {len(tag_names)} tags: {', '.join(tag_names)}")
        
        # Resolve to IDs
        tag_ids = []
        for name in tag_names:
            tid = client.get_or_create_tag_id(name)
            if tid:
                tag_ids.append(tid)
        
        if not tag_ids:
            print("  No tags to add.")
            continue

        # Find the Page
        # Try slug first (cleaner)
        slug = item.get('slug')
        if not slug and full_data:
            slug = full_data.get('slug')
            
        page = None
        if slug:
             page = client.find_page_by_slug(slug)
        
        if not page:
             # Fallback to title search
             page = client.find_page_by_title(item['title'])

        if page:
            print(f"  Found Page ID: {page['id']}")
            # Update
            if client.update_page_tags(page['id'], tag_ids):
                print("  ✅ Tags updated successfully.")
                success_count += 1
            else:
                print("  ❌ Failed to update tags.")
                fail_count += 1
        else:
            print("  ⚠️ Page not found on WordPress.")
            fail_count += 1
            
        # Rate limit friendly
        # time.sleep(0.5) 

    print("\n" + "="*30)
    print(f"Done. Updated: {success_count}, Failed/Skipped: {fail_count}")

if __name__ == "__main__":
    main()
