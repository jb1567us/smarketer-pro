import json
import urllib.request
from PIL import Image
from io import BytesIO
import math
import ssl

# Ignore SSL errors for scraping/downloading
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

ARTWORK_FILE = r'C:\sandbox\esm\artwork_data.json'

# Defined Color Palette for Tagging
COLOR_MAP = {
    "Red": (255, 0, 0),
    "Blue": (0, 0, 255),
    "Green": (0, 128, 0),
    "Yellow": (255, 255, 0),
    "Orange": (255, 165, 0),
    "Purple": (128, 0, 128),
    "Black": (30, 30, 30), # Not pure black to catch dark greys
    "White": (240, 240, 240), # Not pure white
    "Grey": (128, 128, 128),
    "Brown": (165, 42, 42),
    "Pink": (255, 192, 203),
    "Turquoise": (64, 224, 208),
    "Gold": (212, 175, 55),
    "Beige": (245, 245, 220)
}

def closest_color(rgb, threshold=100):
    r, g, b = rgb
    min_dist = float('inf')
    found_color = None
    
    for name, val in COLOR_MAP.items():
        cr, cg, cb = val
        dist = math.sqrt((r - cr)**2 + (g - cg)**2 + (b - cb)**2)
        if dist < min_dist:
            min_dist = dist
            found_color = name
            
    if min_dist < threshold:
        return found_color
    return None

def analyze_image(url):
    try:
        # User-Agent to avoid 403
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            data = response.read()
            
        img = Image.open(BytesIO(data))
        img = img.convert('RGB')
        img = img.resize((150, 150)) # Speed up
        
        # Quantize to 5 colors
        q_img = img.quantize(colors=5)
        palette = q_img.getpalette()[:15] # 5 colors * 3 channels
        
        detected = set()
        
        # Check each of the 5 dominant colors
        for i in range(0, len(palette), 3):
            rgb = tuple(palette[i:i+3])
            # Filter out extreme muted/background if needed, but for now take all
            color_name = closest_color(rgb, threshold=120) # Broad threshold
            if color_name:
                detected.add(color_name)
                
        return list(detected)
        
    except Exception as e:
        print(f"Error analyzing {url}: {e}")
        return []

# MAIN
print("Loading artwork data...")
with open(ARTWORK_FILE, 'r', encoding='utf-8') as f:
    artworks = json.load(f)

print(f"Analyzing {len(artworks)} artworks...")
updated_count = 0

for i, art in enumerate(artworks):
    if 'detected_tags' in art: 
        # Skip if already done? Or force redo if user asked? 
        # Let's force redo or check if empty
        pass
    
    image_url = art.get('image_url')
    if not image_url:
        print(f"[{i+1}/{len(artworks)}] Skipping {art['title']} (No Image)")
        continue
        
    print(f"[{i+1}/{len(artworks)}] Analyzing: {art['title']}...")
    
    # Analyze
    colors = analyze_image(image_url)
    
    if colors:
        print(f"  -> Found: {', '.join(colors)}")
        art['detected_colors'] = colors
        updated_count += 1
    else:
        print("  -> No distinct colors found.")

# Save
print("Saving updated data...")
with open(ARTWORK_FILE, 'w', encoding='utf-8') as f:
    json.dump(artworks, f, indent=4, ensure_ascii=False)

print(f"Done. Updated {updated_count} artworks.")
