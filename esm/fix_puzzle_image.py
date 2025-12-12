import json

# Load artwork data
with open(r'C:\sandbox\esm\artwork_data.json', 'r', encoding='utf-8') as f:
    artworks = json.load(f)

# Find Puzzle
puzzle = None
for art in artworks:
    if 'puzzle' in art.get('title', '').lower() and art.get('title', '').lower() == 'puzzle':
        puzzle = art
        break

if puzzle:
    print("Found Puzzle artwork:")
    print(f"  Title: {puzzle.get('title')}")
    print(f"  Image URL: {puzzle.get('image_url', 'MISSING')}")
    print(f"  Saatchi URL: {puzzle.get('saatchi_url')}")
    
    # Expected image URL based on pattern
    expected_url = "https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/PuzzlePainting.jpg"
    
    if not puzzle.get('image_url'):
        print(f"\n⚠️ Image URL is missing!")
        print(f"Expected: {expected_url}")
        
        # Update
        puzzle['image_url'] = expected_url
        
        # Save
        with open(r'C:\sandbox\esm\artwork_data.json', 'w', encoding='utf-8') as f:
            json.dump(artworks, f, indent=4, ensure_ascii=False)
        
        print("\n✅ Updated artwork_data.json with image URL")
    else:
        print(f"\nImage URL exists: {puzzle['image_url']}")
else:
    print("Puzzle artwork not found in data")
