import requests
import json
import re

TARGETS = [
    "A Day at the Lake", "A day at the beach", "A day at the park", "Abstract Landscape",
    "Gold Series 007", "Gold Series 008", "Gold Series 009", "Gold Series 010", "Gold Series 011",
    "In the Dark Painting", "Red Planet", "Sunset Glacier Painting", "Warm Glacier Painting"
]

def get_saatchi_image(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=10)
        # simplistic regex for og:image
        m = re.search(r'<meta property="og:image" content="(.*?)"', r.text)
        if m:
            return m.group(1)
            
        # fallback to looking for image in json-ld or similar?
        # let's try generic img tag search if og fail
        return None
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

with open('artwork_data.json', 'r', encoding='utf-8') as f:
    artworks = json.load(f)

updated = 0
for art in artworks:
    title = art.get('title', '')
    match = False
    for t in TARGETS:
        if t.lower() in title.lower():
            match = True
            break
            
    if match:
        print(f"Processing {title}...")
        saatchi = art.get('saatchi_url')
        if saatchi:
            img_url = get_saatchi_image(saatchi)
            if img_url:
                print(f" -> Found Image: {img_url}")
                art['image_url'] = img_url # Update!
                updated += 1
            else:
                print(" -> No image found on Saatchi page")
        else:
            print(" -> No Saatchi URL")

if updated > 0:
    with open('artwork_data.json', 'w', encoding='utf-8') as f:
        json.dump(artworks, f, indent=4)
    print(f"Saved {updated} fixes to artwork_data.json")
else:
    print("No updates made.")
