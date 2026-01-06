import json
import difflib
import os

# 1. Load Data
import requests

# 1. Load Data
with open('artwork_data.json', 'r', encoding='utf-8') as f:
    artworks = json.load(f)

print("Fetching server index...")
try:
    r = requests.get('https://elliotspencermorgan.com/get_image_index.php', timeout=30)
    server_files = r.json()
    print(f"Fetched {len(server_files)} files from server.")
except Exception as e:
    print(f"Failed to fetch index: {e}")
    server_files = []

# Filter for full-res images (not thumbnails like -150x150, -300x300 etc)
# Exception: if it's the only one available
full_res_candidates = []
for file in server_files:
    path = file['path']
    # Simplified logic: ignore if it looks like a resize (e.g. ends in -XxY.jpg)
    # But some might be legit. Let's keep all, but prioritize ones without dimensions.
    # Actually, the user wants '11-holdingspace-originals', so verify that path segment.
    if '11-holdingspace-originals' in path:
        file['is_holding'] = True
    else:
        file['is_holding'] = False
        
    # Check for dimension suffix pattern -100x100.jpg
    parts = path.rsplit('-', 1)
    if len(parts) > 1 and 'x' in parts[1] and '.' in parts[1]:
        # rough check
        file['is_thumb'] = True
    else:
        file['is_thumb'] = False
    
    # Store clean name for matching
    # Remove file extension and hyphens
    basename = os.path.splitext(file['name'])[0]
    # Remove -768x1024 etc if thumb
    if file['is_thumb']:
        basename = basename.rsplit('-', 1)[0]
    
    file['clean_name'] = basename.lower().replace('-', ' ').replace('_', ' ').replace('painting', '').replace('sculpture', '').strip()

# 2. Map and Update
print(f"Mapping {len(artworks)} artworks to {len(server_files)} files...")
updated_count = 0

for art in artworks:
    title = art.get('title', '').lower().replace('-', ' ').strip()
    slug = art.get('slug', '').replace('-', ' ')
    
    best_score = 0
    best_match = None
    
    # Simple fuzzy search
    for file in server_files:
        score = 0
        fname = file['clean_name']
        
        # Exact title match
        if title == fname:
            score += 100
        # Title in filename
        elif title in fname:
            score += 80
        # Filename in title
        elif fname in title:
            score += 70
        # Slug match
        elif slug == fname:
            score += 90
            
        # Prioritize Holding Space
        if file['is_holding']:
            score += 5
            
        # Penalize thumbs
        if file['is_thumb']:
            score -= 10
            
        # Boost largest files
        if file['size'] > 100000: # >100KB
            score += 5
            
        if score > best_score:
            best_score = score
            best_match = file
            
    if best_score > 60: # Threshold
        new_url = "https://elliotspencermorgan.com/" + best_match['path']
        art['image_url'] = new_url
        updated_count += 1
        # print(f"Matched: '{title}' -> {best_match['name']} (Score: {best_score})")

print(f"Updated {updated_count} artworks with verified URLs.")

# 3. Save
with open('artwork_data.json', 'w', encoding='utf-8') as f:
    json.dump(artworks, f, indent=4)
