
import json
import re

filepath = 'c:/sandbox/esm/collections_data.json'

with open(filepath, 'r', encoding='utf-8') as f:
    data = json.load(f)

collection_key = 'sculpture-collection'
updated_count = 0

if collection_key in data:
    artworks = data[collection_key]['artworks']
    for art in artworks:
        link = art.get('link', '')
        # Check for the bad date pattern
        if '/2025/09/25/' in link:
            slug = art.get('slug', '')
            if slug:
                new_link = f"https://elliotspencermorgan.com/{slug}/"
                print(f"Fixing '{art.get('title')}':")
                print(f"  Old: {link}")
                print(f"  New: {new_link}")
                art['link'] = new_link
                updated_count += 1
            else:
                print(f"WARNING: '{art.get('title')}' has bad link but NO slug!")

    if updated_count > 0:
        print(f"\nUpdated {updated_count} links. Saving...")
        # Write back to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print("Done.")
    else:
        print("No bad links found.")
else:
    print(f"Collection '{collection_key}' not found.")
