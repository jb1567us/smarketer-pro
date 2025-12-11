import json

# Fix image URLs to use hyphens instead of underscores
# This is refined to match the user's confirmation of "all hyphens"
with open('artwork_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("Fixing image URLs to use hyphens...")
fixed_count = 0

for item in data:
    if 'image_url' in item:
        old_url = item['image_url']
        filename = old_url.split('/')[-1]
        
        # Replace underscores with hyphens
        new_filename = filename.replace('_', '-')
        
        # FIX: Ensure no separator before "Painting" as per user instruction
        # "did not have a space a - or an _between the word painting and the name of it"
        # Example: A-Day-at-the-LakePainting.jpg
        new_filename = new_filename.replace('-Painting.jpg', 'Painting.jpg')
        new_filename = new_filename.replace('_Painting.jpg', 'Painting.jpg')
        new_filename = new_filename.replace(' Painting.jpg', 'Painting.jpg')
        
        new_url = old_url.replace(filename, new_filename)
        
        if old_url != new_url:
            print(f"  {filename} -> {new_filename}")
            item['image_url'] = new_url
            fixed_count += 1

print(f"\nFixed {fixed_count} image URLs")

with open('artwork_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4)

print("✅ Saved updated artwork_data.json")
