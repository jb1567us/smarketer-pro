import json
import requests
import os
import difflib

# Load broken images
with open('c:/sandbox/esm/broken_images.json', 'r') as f:
    broken_list = json.load(f)

# Load artwork data
# Try root path first, then webhost-automation
json_path = 'c:/sandbox/esm/artwork_data.json'
if not os.path.exists(json_path):
    json_path = 'c:/sandbox/esm/webhost-automation/remote_artwork_data.json'

with open(json_path, 'r', encoding='utf-8') as f:
    artwork_data = json.load(f)

# Prepare map for fast lookup? Titles might be fuzzy.
# Create a title -> item map. Normalizing titles (lowercase, strip 'Painting', 'Collage', 'Sculpture', 'Limited Edition', etc.)
def normalize_title(t):
    t = t.lower().replace(u'\u2013', '-').replace(u'\u2014', '-')
    # Remove common suffixes for cleaner matching
    for suffix in [' painting', ' sculpture', ' collage', ' installation', ' restricted', ' limited edition of 1', ' - limited edition of 1']:
        t = t.replace(suffix, '')
    return t.strip()

artwork_map = {}
for item in artwork_data:
    nt = normalize_title(item.get('title', ''))
    if nt:
        artwork_map[nt] = item

print(f"Loaded {len(broken_list)} broken items and {len(artwork_data)} artwork entries.")
print("-" * 60)
print(f"{'Broken Title':<40} | {'JSON Match':<30} | {'JSON Image URL Status'}")
print("-" * 60)

for broken in broken_list:
    original_title = broken['title']
    nt = normalize_title(original_title)
    
    match = artwork_map.get(nt)
    
    # If no exact match, try close match
    if not match:
        matches = difflib.get_close_matches(nt, artwork_map.keys(), n=1, cutoff=0.8)
        if matches:
            match = artwork_map[matches[0]]
    
    if match:
        json_url = match.get('image_url', 'No URL')
        status = "N/A"
        if json_url and json_url.startswith('http'):
            try:
                r = requests.head(json_url, timeout=3)
                status = str(r.status_code)
            except:
                status = "Error"
        print(f"{original_title[:38]:<40} | {match['title'][:28]:<30} | {status} ({json_url})")
    else:
        print(f"{original_title[:38]:<40} | {'NO MATCH':<30} | N/A")

print("-" * 60)
