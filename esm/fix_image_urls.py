import json

# Fix image URLs to use hyphens instead of underscores
with open('artwork_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("Fixing image URLs to use hyphens...")
fixed_count = 0

for item in data:
    if 'image_url' in item:
        old_url = item['image_url']
        # Extract filename from URL
        filename = old_url.split('/')[-1]
        
        # Replace underscores with hyphens in filename
        new_filename = filename.replace('_', '-')
        
        # Build new URL
        new_url = old_url.replace(filename, new_filename)
        
        if old_url != new_url:
            print(f"  {filename} -> {new_filename}")
            item['image_url'] = new_url
            fixed_count += 1

print(f"\nFixed {fixed_count} image URLs")

# Save updated data
with open('artwork_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4)

print("✅ Saved updated artwork_data.json")
