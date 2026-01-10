import json

# Fix image URLs to match the SERVER EVIDENCE (Underscores, specific casing)
with open('artwork_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("Fixing image URLs to match FTP listing...")
fixed_count = 0

for item in data:
    if 'image_url' in item:
        old_url = item['image_url']
        filename = old_url.split('/')[-1]
        
        # 1. Base Strategy: Use Underscores, No separator before Painting
        # Example: Blue_StormPainting.jpg
        
        # Start fresh from the slug or title to be sure? 
        # No, modify existing filename is safer, just flip - to _
        
        new_filename = filename.replace('-', '_')
        
        # Ensure no separator before "Painting.jpg"
        new_filename = new_filename.replace('_Painting.jpg', 'Painting.jpg')
        new_filename = new_filename.replace(' Painting.jpg', 'Painting.jpg')
        
        # 2. Specific Casing Fixes based on FTP List
        if "Gold Screen" in item['title'] or "Gold Series" in item['title']:
            # FTP shows: GOLD_SERIES_001Painting.jpg
            # My data has: Gold_Series_011Painting.jpg
            # So I should make it ALL CAPS for the title part?
            # Wait, list has GOLD_SERIES_001. My item is 011.
            # Assuming 011 is also caps.
            new_filename = new_filename.upper().replace('PAINTING.JPG', 'Painting.jpg')
        
        # List shows "PortalPainting.jpg" (Portal) - Capital P
        # List shows "Portal_2Painting.jpg" (Portal 2) - Underscore?
        if item['title'] == "Portal 2":
             # My data might have Portal_2 or Portal-2.
             # Ensure it is Portal_2Painting.jpg
             new_filename = "Portal_2Painting.jpg"

        new_url = old_url.replace(filename, new_filename)
        
        if old_url != new_url:
            print(f"  {filename} -> {new_filename}")
            item['image_url'] = new_url
            fixed_count += 1

print(f"\nFixed {fixed_count} image URLs")

with open('artwork_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4)

print("✅ Saved updated artwork_data.json (Underscore Edition)")
