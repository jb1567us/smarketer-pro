import json
import os

path = 'c:/sandbox/esm/artwork_data.json'

with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Loaded {len(data)} items.")

# Verify Sheet Music exists (sanity check)
sheet_music = next((item for item in data if 'Sheet Music' in item.get('title', '')), None)
if sheet_music:
    print("Sanity Check: 'Sheet Music' found.")
else:
    print("Sanity Check: 'Sheet Music' NOT FOUND! File might be corrupted or missing data.")

# Find Pieces of Red
to_remove = []
for item in data:
    title = item.get('title', '')
    if 'Pieces of Red' in title:
        print(f"Found match: {title}")
        to_remove.append(item)

if not to_remove:
    print("No 'Pieces of Red' found.")
else:
    for item in to_remove:
        data.remove(item)
    print(f"Removed {len(to_remove)} items.")
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    print("Saved updated artwork_data.json")

# Verify removal
with open(path, 'r', encoding='utf-8') as f:
    data_new = json.load(f)
    if not any('Pieces of Red' in i.get('title', '') for i in data_new):
        print("Verification: 'Pieces of Red' is gone.")
    else:
        print("Verification: 'Pieces of Red' still present!")
