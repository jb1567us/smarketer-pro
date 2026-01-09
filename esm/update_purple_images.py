import json
import shutil
import os

filename = 'artwork_data.json'
backup = 'artwork_data.backup.json'

if not os.path.exists(filename):
    print(f"Error: {filename} not found.")
    exit(1)

shutil.copy(filename, backup)
print(f"Backed up {filename} to {backup}")

try:
    with open(filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
except Exception as e:
    print(f"Error loading JSON: {e}")
    exit(1)

changed = False
count = 0
for item in data:
    title = item.get('title', '')
    if 'Purple' in title:
        old_url = item.get('image_url', '')
        # Pattern match: contains /2025/11/ but NOT holdingspace
        if '/2025/11/' in old_url and '-holdingspace-' not in old_url:
             new_url = old_url.replace('/2025/11/', '/2025/11-holdingspace-originals/')
             print(f"Updating {title}:\n  Old: {old_url}\n  New: {new_url}")
             item['image_url'] = new_url
             changed = True
             count += 1

if changed:
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    print(f"SUCCESS: Updated {count} items in {filename}")
else:
    print("No changes required. Pattern not found or already updated.")
