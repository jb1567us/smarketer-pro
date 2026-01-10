import json
import shutil
import sys

# Paths
collections_path = 'collections_data.json'
artwork_path = 'artwork_data.json'

try:
    with open(collections_path, 'r') as f:
        col_data = json.load(f)
    with open(artwork_path, 'r') as f:
        art_data = json.load(f)
except Exception as e:
    print(f"Error loading files: {e}")
    sys.exit(1)

# Build map of New Descriptions from Collections
# Keys: slug or title? Title is safer if unique, but slug is best.
# Let's map SLUG -> Description
description_map = {}

# Iterate over collections
for col_slug, col in col_data.items():
    if not isinstance(col, dict) or 'artworks' not in col: continue
    
    for aw in col['artworks']:
        slug = aw.get('slug')
        desc = aw.get('description')
        if slug and desc:
            description_map[slug] = desc

print(f"Found {len(description_map)} new descriptions in collections_data.json")

# Update artwork_data.json
updated_count = 0
for aw in art_data:
    slug = aw.get('slug')
    # fallback to title if slug missing?
    
    if slug in description_map:
        # Only update if different or missing
        if aw.get('description') != description_map[slug]:
            aw['description'] = description_map[slug]
            updated_count += 1
    # Check by Title as fallback
    else:
        title = aw.get('title')
        # ... logic if needed, but slug should suffice for 99%

# Save
with open(artwork_path, 'w') as f:
    json.dump(art_data, f, indent=4)

print(f"Synced {updated_count} descriptions to artwork_data.json")
