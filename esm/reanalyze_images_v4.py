import json
import os
import sys
import math
import urllib.request
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

try:
    from PIL import Image
except ImportError:
    # Just in case
    os.system(f"{sys.executable} -m pip install Pillow")
    from PIL import Image

DATA_FILE = r'C:\sandbox\esm\artwork_data.json'
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

# IMPROVED PALETTE to separate Red from Brown
# And catch accents
PALETTE = {
    'Red': (255, 0, 0),
    'Dark Red': (139, 0, 0), # Will map to Red
    'Green': (0, 128, 0),
    'Blue': (0, 0, 255),
    'Dark Blue': (0, 0, 139), # Will map to Blue
    'Yellow': (255, 255, 0),
    'Orange': (255, 165, 0),
    'Purple': (128, 0, 128),
    'Pink': (255, 192, 203),
    'Black': (0, 0, 0),
    'White': (255, 255, 255),
    'Grey': (128, 128, 128),
    'Brown': (101, 67, 33), # Earthy brown (Mud)
    'Gold': (212, 175, 55),
    'Silver': (192, 192, 192),
    'Beige': (245, 245, 220),
    'Turquoise': (64, 224, 208)
}

COLOR_ALIASES = {
    'Dark Red': 'Red',
    'Dark Blue': 'Blue'
}

def get_closest_color_name(rgb):
    min_dist = float('inf')
    closest = None
    r, g, b = rgb
    for name, (pr, pg, pb) in PALETTE.items():
        dist = math.sqrt((r-pr)**2 + (g-pg)**2 + (b-pb)**2)
        if dist < min_dist:
            min_dist = dist
            closest = name
    return closest

def analyze_image(url):
    try:
        filename = "temp_img_v4.jpg"
        urllib.request.urlretrieve(url, filename)
        
        img = Image.open(filename)
        img = img.resize((150, 150))
        img = img.convert('RGB')
        
        # High sensitivity quantization
        result = img.quantize(colors=12).convert('RGB')
        colors = result.getcolors(150*150)
        
        # Aggregate counts by Name (handling aliases)
        color_counts = {}
        
        for count, rgb in colors:
            raw_name = get_closest_color_name(rgb)
            # Map alias
            final_name = COLOR_ALIASES.get(raw_name, raw_name)
            
            color_counts[final_name] = color_counts.get(final_name, 0) + count
            
        # Sort by pixel count
        sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Take Top 4
        final_tags = [name for name, count in sorted_colors[:4]]
        
        return final_tags
        
    except Exception as e:
        return []

print(f"Re-analyzing {len(data)} artworks with V4 Palette...")
updated_count = 0

for item in data:
    if not item.get('image_url'):
        continue
    
    tags = analyze_image(item['image_url'])
    
    if tags:
        item['detected_colors'] = tags
        updated_count += 1
        
        if item['title'] == 'Portal':
            print(f"DEBUG PORTAL V4: {tags}")
            
    if updated_count % 30 == 0:
        print('.', end='', flush=True)

print(f"\nSaving {updated_count} updates...")
with open(DATA_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4)
print("Done.")
