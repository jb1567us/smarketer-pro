import json

json_path = 'collections_data.json'
with open(json_path, 'r') as f:
    data = json.load(f)

collection_slug = 'minimalist-abstract'
target_title = "No Public Shrooms Limited Edition of 1"

if collection_slug in data:
    collection = data[collection_slug]
    if 'artworks' in collection:
        original_count = len(collection['artworks'])
        
        # Filter removal
        new_artworks = []
        for aw in collection['artworks']:
            title = aw.get('title', '')
            # Case-insensitive check
            if target_title.lower() not in title.lower():
                new_artworks.append(aw)
        
        collection['artworks'] = new_artworks
        
        diff = original_count - len(new_artworks)
        print(f"Removed {diff} items matching '{target_title}' from {collection['title']}")
        
        if diff > 0:
            with open(json_path, 'w') as f:
                json.dump(data, f, indent=4)
            print("Updated collections_data.json")
        else:
            print("No matching items found in this collection.")
else:
    print(f"Collection '{collection_slug}' not found.")
