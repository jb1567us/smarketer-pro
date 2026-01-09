import json
import requests
from bs4 import BeautifulSoup
import time
import random
import sys

# Load Data
json_path = 'collections_data.json'
try:
    with open(json_path, 'r') as f:
        data = json.load(f)
except Exception as e:
    print(f"Error loading JSON: {e}")
    sys.exit(1)

# Target collections to update
target_collections = [
    'gold-collection',
    'blue-turquoise-collection',
    'oversized-statement-pieces',
    'sculpture-collection',
    'pattern-geometric',
    'minimalist-abstract',
    'neutral-tones'
]

# Helper: Generate "AI" Descriptive Analysis
def generate_ai_analysis(aw):
    title = aw.get('title', 'Untitled')
    year = aw.get('year') or ''
    mediums = aw.get('mediumsDetailed') or 'Mixed Media'
    styles = aw.get('styles') or 'Abstract'
    width = aw.get('width') or ''
    height = aw.get('height') or ''
    colors = aw.get('detected_colors', [])
    
    # Orientation
    orientation = "composition"
    if width and height:
        try:
            w = float(width)
            h = float(height)
            if w > h * 1.2: orientation = "panoramic landscape"
            elif h > w * 1.2: orientation = "vertical structure"
            else: orientation = "balanced composition"
        except: pass

    # Color string
    color_desc = ""
    if colors:
        c_list = [c.lower() for c in colors[:3]]
        if len(c_list) > 1:
            color_desc = f"dominated by {', '.join(c_list[:-1])} and {c_list[-1]}"
        else:
            color_desc = f"centered around {c_list[0]}"
    
    # Sentences
    templates = [
        f"This {year} {mediums.lower()} piece, \"{title},\" explores themes of {styles.lower()}.",
        f"A stunning example of {styles.split(',')[0].lower()}, \"{title}\" features a {orientation}.",
        f"In \"{title},\" the artist utilizes {mediums.lower()} to create a dynamic visual experience."
    ]
    s1 = random.choice(templates)
    
    s2 = "" 
    if color_desc:
        s2 = f"The work is {color_desc}, adding emotional depth and resonance."
    else:
        s2 = "The composition invites the viewer to look beyond the surface."

    s3 = "Its intricate details and textured layers make it a compelling addition to any contemporary space."

    return f"{s1} {s2} {s3}"

# Scraper Helper
def fetch_saatchi_description(url):
    if not url or 'saatchiart.com' not in url:
        return None
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            # Selectors based on Saatchi structure inspection (might need adjustment)
            # Typically in a div with formatting
            # Searching for "About The Artwork" header's sibling or container
            
            # Try specific class (often changes, so we search by text content mostly)
            # But let's look for known containers
            desc_div = soup.find('div', {'itemprop': 'description'}) # Common schema.org tag
            if desc_div:
                return desc_div.get_text(strip=True)
            
            # Fallback: Find "Description" text and get parent/next sibling
            # This is brittle but standard for scraping
            for h in soup.find_all(['h3', 'h4', 'strong']):
                if "Description" in h.get_text() or "About The Artwork" in h.get_text():
                    # Get the next text block
                    content = h.find_next_sibling('div') or h.parent.find_next_sibling('div')
                    if content:
                        return content.get_text(strip=True)
            
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        return None
    
    return None

# Main Loop
count = 0
for slug in target_collections:
    if slug not in data: continue
    print(f"Processing {slug}...")
    
    collection = data[slug]
    artworks = collection.get('artworks', [])
    
    for aw in artworks:
        # Check if already has a custom description to skip re-scraping
        current_desc = aw.get('description', '')
        if current_desc and len(current_desc) > 250 and "explores themes of" in current_desc: 
             continue

        saatchi_url = aw.get('saatchi_url', '')
        
        # 1. Scrape
        scraped_text = fetch_saatchi_description(saatchi_url)
        time.sleep(0.5) # Be nice
        
        # 2. AI Generate
        ai_text = generate_ai_analysis(aw)
        
        # 3. Combine
        final_desc = ""
        if scraped_text:
             # Clean up scraped text (often has "Original ...")
             final_desc += scraped_text + "\n\n"
        
        final_desc += ai_text
        
        aw['description'] = final_desc
        count += 1
        if count % 5 == 0: print(f"Updated {count} descriptions...")

# Save
with open(json_path, 'w') as f:
    json.dump(data, f, indent=4)

print(f"DONE. Updated {count} artworks.")
