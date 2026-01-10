import json
import os
import sys
import math
import urllib.request
import ssl

# Bypass SSL verify context
ssl._create_default_https_context = ssl._create_unverified_context

# Try importing PIL
try:
    from PIL import Image
except ImportError:
    print("CRITICAL: Pillow (PIL) is not installed. Installing...")
    os.system(f"{sys.executable} -m pip install Pillow")
    from PIL import Image

# 1. Load Data
DATA_FILE = r'C:\sandbox\esm\artwork_data.json'
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

# 2. Color Palette Map (R, G, B)
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
    'Gold': (212, 175, 55), # Approximate
    'Silver': (192, 192, 192),
    'Beige': (245, 245, 220),
    'Turquoise': (64, 224, 208)
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
        # Download temp
        filename = "temp_img.jpg"
        urllib.request.urlretrieve(url, filename)
        
        img = Image.open(filename)
        img = img.resize((150, 150)) # Resize for speed
        img = img.convert('RGB')
        
        # Get simplified palette (e.g. 5 colors)
        # Using quantization
        result = img.quantize(colors=5).convert('RGB')
        
        # Get dominant colors
        # Histogram
        colors = result.getcolors(150*150)
        # colors is list of (count, (r,g,b))
        
        detected = set()
        
        # Sort by count desc
        colors.sort(key=lambda x: x[0], reverse=True)
        
        # Take top 3-4
        current_names = set()
        for count, rgb in colors[:5]:
            name = get_closest_color_name(rgb)
            # Skip White/Black if they are minor? optional.
            # But let's include them.
            detected.add(name)
            
        return list(detected)
        
    except Exception as e:
        print(f"FAILED {url}: {e}")
        return []

# 3. Process
print(f"Analyzing {len(data)} artworks...")
updated_count = 0

for item in data:
    if not item.get('image_url'):
        continue
        
    # Skip if we already have GOOD data?
    # User said "Red tag missing" so we trust NO ONE.
    # Re-run ALL.
    # But for speed in this demo, let's prioritize ones missing colors first?
    # Or just run all. 160 images takes ~2 mins.
    
    print(f"Processing: {item['title']}...", end='')
    
    # Check if image matches "Red Planet" for special debug
    # title = item['title'].lower()
    
    colors = analyze_image(item['image_url'])
    if colors:
        item['detected_colors'] = colors
        updated_count += 1
        print(f" Found: {colors}")
    else:
        print(" No colors found.")

# 4. Save
print(f"\nSaving {updated_count} updates to {DATA_FILE}")
with open(DATA_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4)
print("Done.")
