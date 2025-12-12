import json
import os
import re

# Load Master URLs based on user provided list
with open(r'C:\sandbox\esm\saatchi_master_urls.json', 'r', encoding='utf-8') as f:
    master_urls = json.load(f)

# Load Existing Inventory
inventory_path = r'C:\sandbox\esm\artwork_data.json'
with open(inventory_path, 'r', encoding='utf-8') as f:
    inventory = json.load(f)

# Normalize URL function
def normalize(url):
    return url.split('?')[0].strip()

# Create Map of Existing Saatchi URLs
existing_map = {}
for item in inventory:
    if item.get('saatchi_url'):
        existing_map[normalize(item['saatchi_url'])] = item

# Identify New Items
new_items_count = 0
updated_inventory = list(inventory)

for url in master_urls:
    norm_url = normalize(url)
    if norm_url not in existing_map:
        # Extract matches
        # Pattern: /art/Type-Title/Id/Id/view
        match = re.search(r'/art/([^/]+)/', norm_url)
        title_raw = match.group(1) if match else "Unknown"
        # Clean title: Type-Title -> Title (mostly)
        # e.g. Painting-Caviar -> Caviar
        params = title_raw.split('-')
        clean_title_words = []
        for p in params:
            if p.lower() in ['painting', 'sculpture', 'collage', 'printmaking', 'installation', 'drawing']:
                continue
            clean_title_words.append(p)
        
        clean_title = ' '.join(clean_title_words).replace('_', ' ')
        
        new_item = {
            "id": f"new_{new_items_count}", # Temp ID
            "title": clean_title,
            "saatchi_url": norm_url,
            "type": "new_from_saatchi"
        }
        updated_inventory.append(new_item)
        new_items_count += 1
        print(f"Found new item: {clean_title}")

print(f"Total new items added: {new_items_count}")
print(f"Total inventory size: {len(updated_inventory)}")

# Save updated inventory
with open(inventory_path, 'w', encoding='utf-8') as f:
    json.dump(updated_inventory, f, indent=4)
