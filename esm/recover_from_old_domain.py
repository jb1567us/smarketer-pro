import json
import requests
import re
import time

BASE_URLS = [
    "https://lookoverhere.xyz/esm/wp-content/uploads/2025/09/",
    "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/",
    "https://lookoverhere.xyz/esm/wp-content/uploads/2025/10/",
    "https://lookoverhere.xyz/esm/wp-content/uploads/2024/09/",
    "https://lookoverhere.xyz/esm/wp-content/uploads/2024/08/",
    "https://lookoverhere.xyz/esm/wp-content/uploads/2024/10/",
    "https://lookoverhere.xyz/esm/wp-content/uploads/2024/11/" 
]

def clean_variations(t):
    # Prepare variations
    clean = t.replace(' Painting', '').replace(' Sculpture', '').replace(' Collage', '').strip()
    underscored = clean.replace(' ', '_')
    hyphened = clean.replace(' ', '-')
    
    # Variations to try
    # 1. Underscored + Painting.jpg (Common: CaviarPainting.jpg)
    # 2. Underscored.jpg
    # 3. Hyphened.jpg
    # 4. TitledCase.jpg (Caviar.jpg)
    # 5. Original Title + Painting.jpg (A_Day_at_the_LakePainting.jpg) (Spaces to underscores)
    
    t_und = t.replace(' ', '_')
    
    vars = [
        f"{underscored}Painting.jpg",
        f"{underscored}Sculpture.jpg",
        f"{underscored}Collage.jpg",
        f"{underscored}.jpg",
        f"{hyphened}.jpg",
        f"{t_und}.jpg",
        f"{t_und}Painting.jpg"
    ]
    return vars

with open('artwork_data.json', 'r', encoding='utf-8') as f:
    artworks = json.load(f)

print(f"Scanning {len(artworks)} artworks against {len(BASE_URLS)} base paths on old server...")

headers = {'User-Agent': 'Mozilla/5.0'}
updated_count = 0
session = requests.Session()

import concurrent.futures

def check_artwork(art):
    # Skip if already good
    if '11-holdingspace-originals' in art.get('image_url', ''):
        return None
        
    title = art.get('title', 'Untitled')
    variations = clean_variations(title)
    
    # We want to stop as soon as we find one.
    # Check bases in order? Or just any? Prefer newer dates?
    # Let's check newer dates first (list order).
    
    for base in BASE_URLS:
        for v in variations:
            url = base + v
            try:
                r = requests.head(url, headers=headers, timeout=1)
                if r.status_code == 200:
                    return (art, url)
            except:
                pass
    return None

print(f"Scanning {len(artworks)} artworks in parallel...")
matches = []

with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
    futures = [executor.submit(check_artwork, art) for art in artworks]
    for future in concurrent.futures.as_completed(futures):
        res = future.result()
        if res:
            art, url = res
            print(f"   -> MATCH: {art['title']} -> ...{url[-30:]}")
            art['image_url'] = url
            updated_count += 1
            
            # Incremental save every 10 updates
            if updated_count % 5 == 0:
                with open('artwork_data.json', 'w', encoding='utf-8') as f:
                    json.dump(artworks, f, indent=4)
                print("   [Saved Progress]")

print(f"Finally Updated {updated_count} artworks.")
with open('artwork_data.json', 'w', encoding='utf-8') as f:
    json.dump(artworks, f, indent=4)
