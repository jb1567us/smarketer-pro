import json
import os

# Paths
scraped_file = r'C:\sandbox\esm\esm-portfolio-dev\scraped_images.json'
artwork_file = r'C:\sandbox\esm\artwork_data.json'

# Load Scraped Data
print(f"Loading scraped images from {scraped_file}...")
with open(scraped_file, 'r', encoding='utf-8') as f:
    scraped_data = json.load(f)

print(f"Loaded {len(scraped_data)} scraped items.")

# Load Artwork Data
with open(artwork_file, 'r', encoding='utf-8') as f:
    artwork_data = json.load(f)

# Create lookup for artwork data by ID (handle both int and string IDs)
artwork_by_id = {}
artwork_by_url = {}

for art in artwork_data:
    artwork_by_id[str(art.get('id'))] = art
    if art.get('saatchi_url'):
        artwork_by_url[art.get('saatchi_url')] = art

# Merge
updated_count = 0
errors = 0

for item in scraped_data:
    image_url = item.get('image_url')
    if not image_url:
        continue

    # Try to find match
    match = None
    
    # Match by ID
    current_id = str(item.get('id'))
    if current_id in artwork_by_id:
        match = artwork_by_id[current_id]
    
    # Match by URL if no ID match
    if not match and item.get('saatchi_url') in artwork_by_url:
        match = artwork_by_url[item.get('saatchi_url')]
    
    if match:
        old_image = match.get('image_url')
        if not old_image or old_image.strip() == "":
            match['image_url'] = image_url
            updated_count += 1
            print(f"Updated: {match['title']} -> {image_url}")
    else:
        print(f"Warning: Could not find match for scraped item: {item.get('title')} (ID: {item.get('id')})")
        errors += 1

# Save
with open(artwork_file, 'w', encoding='utf-8') as f:
    json.dump(artwork_data, f, indent=4, ensure_ascii=False)

print(f"\n=== MERGE COMPLETE ===")
print(f"Updated {updated_count} artworks with new images.")
print(f"Errors: {errors}")
