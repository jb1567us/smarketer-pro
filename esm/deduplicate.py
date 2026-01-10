import json
import os

# Load raw inventory
raw_data = []
files = [r'C:\sandbox\esm\full_wordpress_inventory_all.json', r'C:\sandbox\esm\full_wordpress_inventory_part2.json']

for file_path in files:
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                raw_data.extend(data)
                print(f"Loaded {len(data)} items from {file_path}")
        except Exception as e:
            print(f"Error loading {file_path}: {e}")

print(f"Total raw count: {len(raw_data)}")

unique_map = {}
duplicates = []

for item in raw_data:
    # 1. Fix Image Domain
    if item.get('image_url') and 'lookoverhere.xyz/esm' in item['image_url']:
        item['image_url'] = item['image_url'].replace('lookoverhere.xyz/esm', 'elliotspencermorgan.com')

    # 2. Key Generation
    clean_title = item['title'].replace(' Painting', '').replace(' Sculpture', '').replace('&#8211;', '-').strip()
    key = item['saatchi_url'] or clean_title.lower()

    if not key:
        continue

    # 3. Deduplication Logic
    if key in unique_map:
        existing = unique_map[key]
        # Prefer PAGE over POST
        if item['type'] == 'page' and existing['type'] != 'page':
            unique_map[key] = item
        elif item['type'] == 'page' and existing['type'] == 'page':
            duplicates.append(item) # Log duplicate
        else:
            pass # Keep existing (page or earlier post)
    else:
        unique_map[key] = item

cleaned_inventory = list(unique_map.values())
print(f"Cleaned count: {len(cleaned_inventory)}")

# Merge into master artwork_data.json
master_data = []
if os.path.exists(r'C:\sandbox\esm\artwork_data.json'):
    with open(r'C:\sandbox\esm\artwork_data.json', 'r', encoding='utf-8') as f:
        try:
            master_data = json.load(f)
        except json.JSONDecodeError:
            master_data = []

# Merge updates
# Load enhanced metadata if available
enhanced_data = []
if os.path.exists(r'C:\sandbox\esm\enhanced_artwork_data.json'):
     with open(r'C:\sandbox\esm\enhanced_artwork_data.json', 'r', encoding='utf-8') as f:
        enhanced_data = json.load(f)
        print(f"Loaded {len(enhanced_data)} enhanced items.")

# 1. Merge enhanced into clean inventory first
for item in cleaned_inventory:
    for enh in enhanced_data:
        if str(item.get('id')) == str(enh.get('id')) or item.get('saatchi_url') == enh.get('saatchi_url'):
            item.update(enh) # Merge rich data into inventory item

# 2. Merge into master
for new_item in cleaned_inventory:
    # Find existing by Saatchi URL OR Title
    existing_idx = -1
    for i, m in enumerate(master_data):
        if (new_item.get('saatchi_url') and m.get('saatchi_url') == new_item['saatchi_url']) or \
           (m.get('title') == new_item['title']):
            existing_idx = i
            break
    
    if existing_idx > -1:
        # Merge fields, preserve manual tagging if any?
        # Actually, new inventory has fresh WP IDs, so we must update ID.
        master_data[existing_idx].update(new_item)
    else:
        master_data.append(new_item)

# Save
with open(r'C:\sandbox\esm\artwork_data.json', 'w', encoding='utf-8') as f:
    json.dump(master_data, f, indent=4)

print("Updated C:\\sandbox\\esm\\artwork_data.json")
