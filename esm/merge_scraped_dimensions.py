import json

# Load the complete scraped data
with open(r'C:\sandbox\esm\enhanced_artwork_data_complete.json', 'r', encoding='utf-8') as f:
    scraped = json.load(f)

# Load existing inventory
with open(r'C:\sandbox\esm\artwork_data.json', 'r', encoding='utf-8') as f:
    inventory = json.load(f)

# Create lookup by saatchi_url
scraped_map = {item['saatchi_url']: item for item in scraped}

# Update existing items with scraped data
updated = 0
for item in inventory:
    if item.get('saatchi_url') in scraped_map:
        # Merge scraped data
        scraped_item = scraped_map[item['saatchi_url']]
        item.update(scraped_item)
        updated += 1

print(f"Updated {updated} items with scraped metadata")
print(f"Total inventory: {len(inventory)}")

# Save
with open(r'C:\sandbox\esm\artwork_data.json', 'w', encoding='utf-8') as f:
    json.dump(inventory, f, indent=4, ensure_ascii=False)
