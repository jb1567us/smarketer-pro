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
    os.system(f"{sys.executable} -m pip install Pillow")
    from PIL import Image

DATA_FILE = r'C:\sandbox\esm\artwork_data.json'
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

PALETTE = {
    'Red': (255, 0, 0),
    'Green': (0, 128, 0),
    'Blue': (0, 0, 255),
    'Yellow': (255, 255, 0),
    'Orange': (255, 165, 0),
    'Purple': (128, 0, 128),
    'Pink': (255, 192, 203),
    'Black': (0, 0, 0),
    'White': (255, 255, 255),
    'Grey': (128, 128, 128),
    'Brown': (165, 42, 42),
    'Gold': (212, 175, 55),
    'Silver': (192, 192, 192),
    'Beige': (245, 245, 220),
    'Turquoise': (64, 224, 208)
}

def get_closest_color_name(rgb):
    min_dist = float('inf')
    closest = None
    r, g, b = rgb
    for name, (pr, pg, pb) in PALETTE.items():
        # Weighted euclidean (human perception approximation)
        # r*0.3, g*0.59, b*0.11 is better for brightness, but for strict color match:
        dist = math.sqrt((r-pr)**2 + (g-pg)**2 + (b-pb)**2)
        if dist < min_dist:
            min_dist = dist
            closest = name
    return closest

def analyze_image(url):
    try:
        filename = "temp_img_v3.jpg"
        urllib.request.urlretrieve(url, filename)
        
        img = Image.open(filename)
        img = img.resize((150, 150))
        img = img.convert('RGB')
        
        # INCREASED SENSITIVITY: 12 colors instead of 5
        result = img.quantize(colors=12).convert('RGB')
        colors = result.getcolors(150*150) # (count, (r,g,b))
        
        # Aggregate counts by Name
        color_counts = {}
        
        for count, rgb in colors:
            name = get_closest_color_name(rgb)
            color_counts[name] = color_counts.get(name, 0) + count
            
        # Sort by total pixel count
        sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Take Top 4
        final_tags = [name for name, count in sorted_colors[:4]]
        
        return final_tags
        
    except Exception as e:
        # print(f"Error {url}: {e}")
        return []

print(f"Re-analyzing {len(data)} artworks with HIGHER sensitivity (Max 4 tags)...")
updated_count = 0

for item in data:
    if not item.get('image_url'):
        continue
    
    # Specific Debug for Portal to verify fix
    is_portal = (item['title'] == 'Portal')
    
    tags = analyze_image(item['image_url'])
    
    if tags:
        item['detected_colors'] = tags
        updated_count += 1
        if is_portal:
            print(f"DEBUG PORTAL: Found {tags}")
    
    # Simple progress
    if updated_count % 20 == 0:
        print(f"{updated_count}...", end='', flush=True)

print(f"\nSaving {updated_count} updates...")
with open(DATA_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4)
print("Done.")
