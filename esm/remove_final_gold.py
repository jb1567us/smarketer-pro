
import json
import os

filepath = 'c:/sandbox/esm/collections_data.json'
# Exact titles found in grep
target_titles = [
    "Start Sign Limited Edition of 1",
    "NO PORKING"
]

with open(filepath, 'r', encoding='utf-8') as f:
    data = json.load(f)

collection_key = 'gold-collection'
if collection_key in data:
    original_count = len(data[collection_key]['artworks'])
    
    new_artworks = []
    removed_count = 0
    
    for item in data[collection_key]['artworks']:
        if item.get('title') in target_titles:
            print(f"Removing '{item.get('title')}'")
            removed_count += 1
        else:
            new_artworks.append(item)
            
    data[collection_key]['artworks'] = new_artworks
    new_count = len(new_artworks)
    
    print(f"Collection '{collection_key}': {original_count} -> {new_count}")
    
    if removed_count > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print("Updated JSON saved.")
    else:
        print("No targets found in this collection.")
else:
    print(f"Collection '{collection_key}' not found.")
