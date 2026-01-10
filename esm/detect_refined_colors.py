import json
import requests
from io import BytesIO
from PIL import Image
import math
import sys
import numpy as np
from sklearn.cluster import KMeans

# --- REFINED COLOR PALETTE (V2) ---
REFINED_PALETTE = {
    # NEUTRALS / BLACKS
    'Obsidian': (20, 20, 20),
    'Ebony': (10, 10, 10),
    'Charcoal': (54, 69, 79),
    'Slate': (112, 128, 144),
    'Graphite': (83, 83, 83),
    'Silver': (192, 192, 192),
    'Platinum': (229, 228, 226),
    'Alabaster': (242, 240, 230),
    'Ivory': (255, 255, 240),
    'Cream': (255, 253, 208),
    'Birch': (240, 226, 195),
    'Pearl': (234, 230, 202),
    'Taupe': (140, 130, 120),
    'Espresso': (75, 54, 33),
    'Sand': (194, 188, 150),
    
    # METALLICS / YELLOWS
    'Gold': (212, 175, 55),
    'Brass': (181, 166, 66),
    'Bronze': (205, 127, 50),
    'Ochre': (204, 119, 34),
    'Amber': (255, 191, 0),
    'Saffron': (244, 196, 48),
    'Canary': (255, 255, 153),
    
    # REDS / PINKS
    'Crimson': (220, 20, 60),
    'Scarlet': (255, 36, 0),
    'Burgundy': (128, 0, 32),
    'Rust': (183, 65, 14),
    'Coral': (255, 127, 80),
    'Terra Cotta': (226, 114, 91),
    'Blush': (222, 93, 131),
    'Mauve': (224, 176, 255),
    
    # BLUES
    'Navy': (0, 0, 128),
    'Midnight': (25, 25, 112),
    'Sapphire': (15, 82, 186),
    'Cobalt': (0, 71, 171),
    'Cerulean': (0, 123, 167),
    'Teal': (0, 128, 128),
    'Turquoise': (64, 224, 208),
    'Ice': (165, 242, 243),
    
    # GREENS
    'Emerald': (80, 200, 120),
    'Forest': (34, 139, 34),
    'Olive': (128, 128, 0),
    'Sage': (150, 160, 130),
    'Moss': (138, 154, 91),
    'Mint': (152, 255, 152),
    'Jade': (0, 168, 107),
    
    # PURPLES
    'Amethyst': (153, 102, 204),
    'Plum': (142, 69, 133),
    'Lavender': (230, 230, 250),
    'Indigo': (75, 0, 130)
}

def get_color_name(rgb):
    r, g, b = rgb
    min_dist = float('inf')
    closest_name = "Unknown"
    for name, val in REFINED_PALETTE.items():
        dr = r - val[0]
        dg = g - val[1]
        db = b - val[2]
        dist = math.sqrt(dr*dr + dg*dg + db*db)
        if dist < min_dist:
            min_dist = dist
            closest_name = name
    return closest_name

def analyze_image_sklearn(url):
    try:
        response = requests.get(url, timeout=10)
        img = Image.open(BytesIO(response.content))
        img = img.convert('RGB')
        
        # Resize to speed up KMeans (200x200 is plenty)
        img = img.resize((150, 150))
        
        # Convert to numpy array of pixels
        img_np = np.array(img)
        pixels = img_np.reshape(-1, 3)
        
        # KMeans
        # Use 6 clusters to capture variety
        kmeans = KMeans(n_clusters=6, random_state=42, n_init=5)
        kmeans.fit(pixels)
        
        # Get centroids
        centers = kmeans.cluster_centers_
        labels = kmeans.labels_
        
        # Count pixels per cluster
        counts = np.bincount(labels)
        
        # Sort centroids by count (dominance)
        sorted_indices = np.argsort(counts)[::-1]
        
        detected = []
        seen_names = set()
        
        for idx in sorted_indices:
            centroid = centers[idx]
            rgb = tuple(map(int, centroid))
            
            name = get_color_name(rgb)
            
            # Simple dedup
            if name not in seen_names:
                detected.append(name)
                seen_names.add(name)
            
            if len(detected) >= 4:
                break
                
        return detected
        
    except Exception as e:
        print(f"Failed to analyze {url}: {e}")
        return []

# --- MAIN ---
json_path = 'collections_data.json'
with open(json_path, 'r') as f:
    data = json.load(f)

count = 0
total_scanned = 0

print("Starting Scikit-learn Color Analysis (KMeans)...")

for col_slug, col in data.items():
    # print(f"Processing {col_slug}...")
    for aw in col.get('artworks', []):
        url = aw.get('image_url') or aw.get('link') or ''
        
        if aw.get('image_url'):
            current = aw.get('detected_colors', [])
            
            # Run Sklearn Analysis
            new_colors = analyze_image_sklearn(aw['image_url'])
            
            if new_colors:
                # Diff check?
                if new_colors != current:
                    if 'Jaguar' in aw.get('title', ''):
                        print(f"** JAGUAR: {current} -> {new_colors}")
                    
                    aw['detected_colors'] = new_colors
                    count += 1
            total_scanned += 1
            
            if total_scanned % 10 == 0:
                print(f"Scanned {total_scanned} images...", end='\r')

print()
with open(json_path, 'w') as f:
    json.dump(data, f, indent=4)

print(f"DONE. Updated {count} artworks using K-Means Clustering.")
