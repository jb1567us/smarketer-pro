import json

json_path = 'collections_data.json'
with open(json_path, 'r') as f:
    data = json.load(f)

slug = 'blue-turquoise-collection'
target_title = 'Blast of Blue on Red'

if slug in data:
    collection = data[slug]
    initial_count = len(collection['artworks'])
    
    # Filter out the target
    collection['artworks'] = [aw for aw in collection['artworks'] if aw.get('title') != target_title]
    
    final_count = len(collection['artworks'])
    
    if initial_count != final_count:
        print(f"Removed '{target_title}' from '{slug}'. Count: {initial_count} -> {final_count}")
    else:
        print(f"Warning: '{target_title}' not found in '{slug}'.")

    with open(json_path, 'w') as f:
        json.dump(data, f, indent=4)
else:
    print(f"Collection '{slug}' not found.")
