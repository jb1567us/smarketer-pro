import json
import re

SERVER_ROOT_PREFIX = "" # PHP will prepend __DIR__ or specific root
URL_PREFIX = "https://elliotspencermorgan.com/"

def clean_filename(title):
    # Same logic as Spec Sheets to ensure predictable naming
    # Replace invalid chars, spaces to underscores?
    # Spec sheets used simple sanitize.
    clean = re.sub(r'[^\w\s-]', '', title).strip().replace(' ', '_')
    return clean

with open('artwork_data.json', 'r', encoding='utf-8') as f:
    artworks = json.load(f)

zip_map = {}

for art in artworks:
    title = art.get('title', 'Untitled')
    image_url = art.get('image_url', '')
    
    if not image_url or 'placeholder' in image_url.lower() or not image_url.startswith('http'):
        continue
        
    # Extract relative path: wp-content/...
    if URL_PREFIX in image_url:
        rel_path = image_url.replace(URL_PREFIX, '')
    elif 'lookoverhere.xyz/esm/' in image_url:
        # Legacy URL - assume it was migrated or exists?
        # Actually, if the JSON still points to lookoverhere, we might have a problem if that server path isn't local.
        # But earlier I said I'd recovered them. Did I update the URLs to elliotspencermorgan.com?
        # No, my recovery script updated specific failed items to lookoverhere.xyz.
        # IF the file is NOT on the live server, PHP cannot zip it from local disk.
        # It would need to download it first.
        # PHP can do `copy($url, $temp)` then zip.
        # I'll flag remote URLs for the PHP script to handle via download.
        rel_path = image_url
    else:
        rel_path = image_url
        
    clean_name = clean_filename(title)
    zip_filename = f"{clean_name}_HighRes.zip"
    
    zip_map[zip_filename] = rel_path

print(f"Mapped {len(zip_map)} items for zipping.")

with open('zip_map.json', 'w', encoding='utf-8') as f:
    json.dump(zip_map, f, indent=4)
