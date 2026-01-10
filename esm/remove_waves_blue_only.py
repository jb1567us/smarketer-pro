import json

json_path = 'collections_data.json'
with open(json_path, 'r') as f:
    data = json.load(f)

collection_slug = 'blue-turquoise-collection'
targets = ["Waves", "Waves Painting"]

if collection_slug in data:
    collection = data[collection_slug]
    if 'artworks' in collection:
        original_count = len(collection['artworks'])
        
        # Filter removal
        new_artworks = []
        for aw in collection['artworks']:
            title = aw.get('title', '')
            # Check if any target string is in the title (case-insensitive)
            # User said "Waves" and "Waves Painting", so checking "Waves" covers both generally
            is_target = False
            for t in targets:
                if t.lower() in title.lower():
                    is_target = True
                    break
            
            if not is_target:
                new_artworks.append(aw)
        
        collection['artworks'] = new_artworks
        
        diff = original_count - len(new_artworks)
        print(f"Removed {diff} items containing 'Waves' from {collection['title']}")
        
        if diff > 0:
            with open(json_path, 'w') as f:
                json.dump(data, f, indent=4)
            print("Updated collections_data.json")
        else:
            print("No 'Waves' items found in this collection.")
else:
    print(f"Collection '{collection_slug}' not found.")
