import json
import os

backup_path = 'c:/sandbox/esm/webhost-automation/remote_artwork_data.json'
target_path = 'c:/sandbox/esm/artwork_data.json'

print("Restoring 'Pieces of Red'...")

# Load Backup
with open(backup_path, 'r', encoding='utf-8') as f:
    backup_data = json.load(f)

# Find Item
item_to_restore = None
for item in backup_data:
    if 'Pieces of Red' in item.get('title', ''):
        item_to_restore = item
        break

if not item_to_restore:
    print("Error: Could not find 'Pieces of Red' in backup!")
    exit(1)

print(f"Found item: {item_to_restore['title']}")

# Load Target
with open(target_path, 'r', encoding='utf-8') as f:
    target_data = json.load(f)

# Check if already exists (avoid dupe)
exists = any('Pieces of Red' in i.get('title', '') for i in target_data)
if exists:
    print("Item already exists in target. Skipping append.")
else:
    target_data.append(item_to_restore)
    # Sort by ID to be tidy? Or just append. Append is safer to not mess up order if it matters.
    # Actually, let's just append.
    
    with open(target_path, 'w', encoding='utf-8') as f:
        json.dump(target_data, f, indent=4)
    print("Restored item to artwork_data.json")
