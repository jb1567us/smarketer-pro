import json
import os

# Load JSON
json_path = 'collections_data.json'
with open(json_path, 'r') as f:
    data = json.load(f)

# Titles to remove (partial match or exact)
targets = [
    "A Day at the Lake",
    "Warm Glacier",
    "Sunset Glacier"
]

def should_remove(artwork):
    title = artwork.get('title', '')
    for t in targets:
        if t.lower() in title.lower():
            return True
    return False

# Iterate and remove
removed_count = 0
for collection_slug, collection in data.items():
    if not isinstance(collection, dict) or 'artworks' not in collection:
        continue
    
    original_count = len(collection['artworks'])
    collection['artworks'] = [aw for aw in collection['artworks'] if not should_remove(aw)]
    new_count = len(collection['artworks'])
    
    if original_count != new_count:
        diff = original_count - new_count
        removed_count += diff
        print(f"Removed {diff} items from {collection['title']}")

# Save
if removed_count > 0:
    with open(json_path, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Total removed: {removed_count}")
    print("Updated collections_data.json")
else:
    print("No items found to remove.")
