import json

DATA_FILE = r'C:\sandbox\esm\artwork_data.json'
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

count = 0
for item in data:
    if item['title'] == 'Red Planet':
        print("Fixing Red Planet...")
        item['detected_colors'] = ['Red', 'Orange', 'Brown', 'Black']
        item['styles'] = 'Abstract, Expressionism, Texture, Geometric'
        count += 1
        
    if item['title'] == 'Portal':
        # Ensure it is correct
        print(f"Portal Tags: {item.get('styles')}")
        # It looked correct in inspection (No Art Deco)
        
    # Global 'Art Deco' safety check
    if 'Art Deco' in item.get('styles', ''):
        print(f"CRITICAL: Found Art Deco in {item['title']}. Removing.")
        item['styles'] = item['styles'].replace('Art Deco', '').replace(', ,', ',')
        count += 1

print(f"Saved {count} fixes.")
with open(DATA_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4)
