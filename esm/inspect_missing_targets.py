import json

TARGETS = [
    "A Day at the Lake", "A day at the beach", "A day at the park", "Abstract Landscape",
    "Gold Series 007", "Gold Series 008", "Gold Series 009", "Gold Series 010", "Gold Series 011",
    "In the Dark Painting", "Red Planet", "Sunset Glacier Painting", "Warm Glacier Painting"
]

with open('artwork_data.json', 'r', encoding='utf-8') as f:
    artworks = json.load(f)

print("Checking targets in data...")
for t in TARGETS:
    found = False
    for art in artworks:
        # fuzzy match title
        if t.lower() in art.get('title', '').lower():
            print(f"\n--- MATCH: {art['title']} ---")
            print(f"Current Image URL: {art.get('image_url')}")
            print(f"Saatchi URL: {art.get('saatchi_url')}")
            found = True
            break
    if not found:
        print(f"\n❌ Could not find data for {t}")
