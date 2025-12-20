
import json
import os

filepath = 'c:/sandbox/esm/collections_data.json'

with open(filepath, 'r', encoding='utf-8') as f:
    data = json.load(f)

collection_key = 'sculpture-collection'
if collection_key in data:
    original_count = len(data[collection_key]['artworks'])
    
    # Filter out Floating Leaves
    new_artworks = [
        item for item in data[collection_key]['artworks'] 
        if item.get('title') != 'Floating Leaves'
    ]
    
    data[collection_key]['artworks'] = new_artworks
    new_count = len(new_artworks)
    
    print(f"Collection '{collection_key}':")
    print(f"Original count: {original_count}")
    print(f"New count: {new_count}")
    
    if original_count != new_count:
        print("Removed 'Floating Leaves'. Saving...")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print("Done.")
    else:
        print("'Floating Leaves' not found in this collection.")
else:
    print(f"Key '{collection_key}' not found.")
