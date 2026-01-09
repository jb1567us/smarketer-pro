import json
import os

# Load scraped data with dimensions
scraped_path = r'C:\sandbox\esm\esm-portfolio-dev\scraped_with_dimensions.json'
if not os.path.exists(scraped_path):
    scraped_path = r'C:\sandbox\esm\scraped_with_dimensions.json'

with open(scraped_path, 'r', encoding='utf-8') as f:
    scraped_data = json.load(f)

print(f"Loaded {len(scraped_data)} items from scraped data")

# Load existing inventory
with open(r'C:\sandbox\esm\artwork_data.json', 'r', encoding='utf-8') as f:
    inventory = json.load(f)

print(f"Loaded {len(inventory)} items from inventory")

# Create lookup by saatchi_url and by ID
scraped_by_url = {item['saatchi_url']: item for item in scraped_data}
scraped_by_id = {str(item['id']): item for item in scraped_data}

# Merge scraped data into inventory
updated = 0
for item in inventory:
    matched = None
    
    # Try matching by saatchi_url first
    if item.get('saatchi_url') and item['saatchi_url'] in scraped_by_url:
        matched = scraped_by_url[item['saatchi_url']]
    # Try matching by ID
    elif str(item.get('id')) in scraped_by_id:
        matched = scraped_by_id[str(item['id'])]
    
    if matched:
        # Update with all scraped fields
        for key in ['year', 'styles', 'mediumsDetailed', 'dimensions', 'frame', 'readyToHang', 'packaging', 'shippingFrom']:
            if key in matched:
                item[key] = matched[key]
        
        # Parse dimensions into width/height/depth
        if matched.get('dimensions'):
            try:
                dim_str = matched['dimensions'].replace(' in', '').strip()
                parts = dim_str.split(' x ')
                if len(parts) >= 2:
                    item['width'] = parts[0].replace(' W', '').strip()
                    item['height'] = parts[1].replace(' H', '').strip()
                if len(parts) >= 3:
                    item['depth'] = parts[2].replace(' D', '').strip()
            except Exception as e:
                print(f"Error parsing dimensions for {item.get('title')}: {e}")
        
        updated += 1

print(f"\nUpdated {updated} items with scraped metadata")
print(f"Total inventory: {len(inventory)}")

# Save updated inventory
with open(r'C:\sandbox\esm\artwork_data.json', 'w', encoding='utf-8') as f:
    json.dump(inventory, f, indent=4, ensure_ascii=False)

print("\nSaved updated artwork_data.json")
