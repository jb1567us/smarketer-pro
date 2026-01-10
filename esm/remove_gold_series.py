
import json
import os

filepath = 'c:/sandbox/esm/collections_data.json'
target_titles = [
    "Gold Series 007",
    "Gold Series 008",
    "Gold Series 009",
    "Gold Series 010",
    "Gold Series 011"
]

with open(filepath, 'r', encoding='utf-8') as f:
    data = json.load(f)

collection_key = 'gold-collection'
if collection_key in data:
    original_count = len(data[collection_key]['artworks'])
    
    new_artworks = []
    removed = 0
    for item in data[collection_key]['artworks']:
        if item.get('title') in target_titles:
            print(f"Removing '{item.get('title')}'")
            removed += 1
        else:
            new_artworks.append(item)
            
    data[collection_key]['artworks'] = new_artworks
    new_count = len(new_artworks)
    
    print(f"Collection '{collection_key}': {original_count} -> {new_count}")
    
    if removed > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print("Detailed saved.")
    else:
        print("No matching items found to remove.")
else:
    print(f"Collection '{collection_key}' not found.")
