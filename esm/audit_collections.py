
import json

filepath = 'c:/sandbox/esm/server_collections_data.json'

with open(filepath, 'r', encoding='utf-8') as f:
    data = json.load(f)

target_title = "Floating Leaves"
found_in = []

for key, collection in data.items():
    print(f"Checking Collection: {key}")
    artworks = collection.get('artworks', [])
    for item in artworks:
        if item.get('title') == target_title:
            found_in.append(key)
            print(f"  FOUND '{target_title}' in '{key}'!")

print("\n--- Summary ---")
if found_in:
    print(f"'{target_title}' is present in: {', '.join(found_in)}")
else:
    print(f"'{target_title}' was NOT found in any collection.")

if 'sculpture-collection' in data:
    count = len(data['sculpture-collection'].get('artworks', []))
    print(f"\n'sculpture-collection' item count: {count}")
    # List titles in sculpture collection for sanity
    print("Titles in sculpture-collection:")
    for item in data['sculpture-collection'].get('artworks', []):
        print(f"- {item.get('title')}")
else:
    print("'sculpture-collection' key missing.")
