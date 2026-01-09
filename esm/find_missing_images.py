import json

# Load artwork data
with open(r'C:\sandbox\esm\artwork_data.json', 'r', encoding='utf-8') as f:
    artworks = json.load(f)

print(f"Scanning {len(artworks)} artworks for missing images...\n")

missing_images = []
found_images = 0

for artwork in artworks:
    image_url = artwork.get('image_url')
    
    # Check if image_url is missing, empty, or None
    if not image_url or image_url.strip() == "":
        missing_images.append({
            'id': artwork.get('id'),
            'title': artwork.get('title'),
            'saatchi_url': artwork.get('saatchi_url')
        })
    else:
        found_images += 1

print(f"=== RESULTS ===")
print(f"Artworks with images: {found_images}")
print(f"Artworks MISSING images: {len(missing_images)}\n")

if missing_images:
    print("List of artworks missing images:")
    for item in missing_images:
        print(f"  - {item['title']} (ID: {item['id']})")
        print(f"    Saatchi: {item['saatchi_url']}")
        print()
else:
    print("✅ All artworks have image URLs.")
