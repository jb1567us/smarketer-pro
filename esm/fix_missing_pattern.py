import json
import requests
import re

TARGETS = [
    "A Day at the Lake", "A day at the beach", "A day at the park", "Abstract Landscape",
    "Gold Series 007", "Gold Series 008", "Gold Series 009", "Gold Series 010", "Gold Series 011",
    "In the Dark Painting", "Red Planet", "Sunset Glacier Painting", "Warm Glacier Painting"
]

BASE_URLS = [
    "https://lookoverhere.xyz/esm/wp-content/uploads/2025/09/",
    "https://lookoverhere.xyz/esm/wp-content/uploads/2025/10/",
    "https://lookoverhere.xyz/esm/wp-content/uploads/2025/11/",
    "https://lookoverhere.xyz/esm/wp-content/uploads/2024/09/",
    "https://lookoverhere.xyz/esm/wp-content/uploads/2024/08/"
]

def clean_title(t):
    # Try different variations
    # 1. "A Day at the Lake" -> "A_Day_at_the_LakePainting.jpg"
    # 2. "A Day at the Lake" -> "A_Day_at_the_Lake.jpg"
    # 3. "Warm Glacier Painting" -> "Warm_GlacierPainting.jpg" (avoid double painting)
    
    t = t.replace(' Painting', '') # Remove Trailing Painting key
    base = t.replace(' ', '_')
    
    variations = [
        f"{base}Painting.jpg",
        f"{base}.jpg",
        f"{base}_Painting.jpg"
    ]
    return variations

with open('artwork_data.json', 'r', encoding='utf-8') as f:
    artworks = json.load(f)

updated = 0
headers = {'User-Agent': 'Mozilla/5.0'}

for art in artworks:
    title = art.get('title', '')
    if any(t.lower() in title.lower() for t in TARGETS):
        print(f"Checking {title}...")
        
        candidates = clean_title(title)
        found_url = None
        
        for base in BASE_URLS:
            if found_url: break
            for c in candidates:
                url = base + c
                try:
                    r = requests.head(url, headers=headers, timeout=5)
                    if r.status_code == 200:
                        print(f" ✅ Found: {url}")
                        found_url = url
                        break
                except:
                    pass
        
        if found_url:
            art['image_url'] = found_url
            updated += 1
        else:
            print(f" ❌ Could not guess URL for {title}")

if updated > 0:
    with open('artwork_data.json', 'w', encoding='utf-8') as f:
        json.dump(artworks, f, indent=4)
    print(f"Saved {updated} fixes.")
else:
    print("No pattern matches found on lookoverhere.xyz.")
