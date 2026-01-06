import json
import os

REMOVE_TITLES = [
    "Puzzle", 
    "Red and Black - Mulch Series Collage",
    "Pieces of Red",
    "City at Night - Mulch Series Collage",
    "Close up - Mulch Series Collage"
]

# 1. Update JSON
with open('artwork_data.json', 'r', encoding='utf-8') as f:
    artworks = json.load(f)

print(f"Original count: {len(artworks)}")

new_artworks = []
removed_ids = []

for art in artworks:
    title = art.get('title', '')
    # Check exact or very close matches
    if title in REMOVE_TITLES:
        print(f"Removing JSON entry: {title}")
        removed_ids.append(title)
        continue
        
    # Also check case-insensitive for safety
    if any(r.lower() == title.lower() for r in REMOVE_TITLES):
        print(f"Removing JSON entry (case-match): {title}")
        removed_ids.append(title)
        continue
        
    new_artworks.append(art)

print(f"New count: {len(new_artworks)}")

with open('artwork_data.json', 'w', encoding='utf-8') as f:
    json.dump(new_artworks, f, indent=4)

# 2. Delete Local Files
DIR = r'C:\sandbox\esm\spec_sheets_v3'
files = os.listdir(DIR)
deleted_files = 0

for f in files:
    # Check if file starts with one of the removed titles
    # Filenames are like "Title_Sheet.pdf" or "123_Title_Sheet.pdf"
    # Actually my generator uses "{Title}_Sheet.pdf" or "{ID}_{Title}_Sheet.pdf" depending on version?
    # V3 Generator uses: f"{clean_title}_Sheet.pdf"
    # clean_title replaces / with - etc.
    
    # Simple check: title in filename
    matches = False
    for title in REMOVE_TITLES:
        # construct likely filename parts
        # "Portal 001 Painting" -> "Portal 001 Painting_Sheet.pdf"
        if title in f:
            matches = True
            break
            
    if matches:
        path = os.path.join(DIR, f)
        try:
            os.remove(path)
            print(f"Deleted file: {f}")
            deleted_files += 1
        except Exception as e:
            print(f"Error deleting {f}: {e}")

print(f"Deleted {deleted_files} local files.")
