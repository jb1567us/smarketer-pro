import json

# Merge enhanced metadata into artwork_data.json

with open('artwork_data.json', 'r', encoding='utf-8') as f:
    master_data = json.load(f)

with open('enhanced_artwork_data.json', 'r', encoding='utf-8') as f:
    new_data = json.load(f)

# Create lookup map for new data
new_data_map = {item['id']: item for item in new_data}

updated_count = 0

for item in master_data:
    item_id = item['id']
    if item_id in new_data_map:
        new_item = new_data_map[item_id]
        
        # Merge fields if they exist
        if 'year' in new_item: item['year'] = new_item['year']
        if 'styles' in new_item: item['styles'] = new_item['styles']
        if 'mediumsDetailed' in new_item: item['mediumsDetailed'] = new_item['mediumsDetailed']
        if 'frame' in new_item: item['frame'] = new_item['frame']
        if 'readyToHang' in new_item: item['readyToHang'] = new_item['readyToHang']
        if 'packaging' in new_item: item['packaging'] = new_item['packaging']
        if 'shippingFrom' in new_item: item['shippingFrom'] = new_item['shippingFrom']
        
        # Saatchi scraper didn't seem to get descriptions in the quick sample, 
        # but if it did, we'd add it.
        if 'description' in new_item:
             item['long_description'] = new_item['description'] # Use specific key for template

        updated_count += 1

print(f"Updated {updated_count} items with enhanced metadata.")

with open('artwork_data.json', 'w', encoding='utf-8') as f:
    json.dump(master_data, f, indent=4)
