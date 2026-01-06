import json

# Load artwork data
with open(r'C:\sandbox\esm\artwork_data.json', 'r', encoding='utf-8') as f:
    artworks = json.load(f)

output_file = r'C:\sandbox\esm\missing_images_report.txt'

missing_images = []
found_images = 0

for artwork in artworks:
    image_url = artwork.get('image_url')
    
    # Check if image_url is missing, empty, or None
    if not image_url or image_url.strip() == "":
        missing_images.append(artwork)
    else:
        found_images += 1

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(f"=== MISSING IMAGES REPORT ===\n")
    f.write(f"Total Artworks: {len(artworks)}\n")
    f.write(f"With Images: {found_images}\n")
    f.write(f"Missing Images: {len(missing_images)}\n\n")
    
    if missing_images:
        f.write("Artworks Missing Images:\n")
        for i, item in enumerate(missing_images, 1):
            title = item.get('title', 'Unknown Title')
            saatchi = item.get('saatchi_url', 'No Saatchi URL')
            f.write(f"{i}. {title}\n")
            f.write(f"   Saatchi: {saatchi}\n")
            f.write(f"   ID: {item.get('id')}\n")
            f.write("\n")

print(f"Report generated: {output_file}")
print(f"Found {len(missing_images)} missing images.")
