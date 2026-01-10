import json

with open(r'C:\sandbox\esm\artwork_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for item in data:
    if item['title'] in ['Red Planet', 'Portal']:
        print(f"--- {item['title']} (ID: {item.get('wordpress_id')}) ---")
        print(f"Styles: {item.get('styles')}")
        print(f"Colors: {item.get('detected_colors')}")
        print("------------------------------------------------")
