import json
from datetime import datetime

# Load artwork data
with open(r'C:\sandbox\esm\artwork_data.json', 'r', encoding='utf-8') as f:
    artworks = json.load(f)

print(f"Total artworks before deduplication: {len(artworks)}\n")

# Group by saatchi_url (primary identifier)
groups_by_url = {}
no_url = []

for artwork in artworks:
    url = artwork.get('saatchi_url')
    if url:
        if url not in groups_by_url:
            groups_by_url[url] = []
        groups_by_url[url].append(artwork)
    else:
        no_url.append(artwork)

# Find duplicates
duplicates = {url: items for url, items in groups_by_url.items() if len(items) > 1}

print(f"Found {len(duplicates)} duplicate groups by Saatchi URL")
print(f"Artworks without Saatchi URL: {len(no_url)}\n")

if duplicates:
    print("Duplicate groups:")
    for url, items in list(duplicates.items())[:10]:  # Show first 10
        print(f"\n  URL: {url}")
        for item in items:
            print(f"    - ID: {item.get('id')}, Type: {item.get('type')}, Date: {item.get('date', 'N/A')}")

# Deduplication strategy: Keep the most complete version
def score_artwork(artwork):
    """Score an artwork by completeness and recency"""
    score = 0
    
    # Prefer pages over posts
    if artwork.get('type') == 'page':
        score += 100
    elif artwork.get('type') == 'post':
        score += 50
    
    # Prefer items with actual numeric IDs over "new_X"
    if isinstance(artwork.get('id'), int):
        score += 50
    
    # Score by data completeness
    important_fields = ['dimensions', 'year', 'mediumsDetailed', 'width', 'height', 'link']
    for field in important_fields:
        if artwork.get(field):
            score += 10
    
    # Prefer items with WordPress link
    if artwork.get('link') and 'elliotspencermorgan.com' in artwork.get('link', ''):
        score += 50
    
    # Prefer items with date (more recent)
    if artwork.get('date'):
        try:
            date_obj = datetime.fromisoformat(artwork['date'].replace('Z', '+00:00'))
            # More recent = higher score (days since 2020)
            days = (date_obj - datetime(2020, 1, 1, tzinfo=date_obj.tzinfo)).days
            score += days // 10  # Small bonus for recency
        except:
            pass
    
    return score

# Deduplicate
deduplicated = []
kept = {}
removed = []

for url, items in groups_by_url.items():
    if len(items) == 1:
        deduplicated.append(items[0])
        kept[url] = items[0]
    else:
        # Score each item
        scored = [(score_artwork(item), item) for item in items]
        scored.sort(reverse=True, key=lambda x: x[0])
        
        # Keep the highest scoring item
        best = scored[0][1]
        deduplicated.append(best)
        kept[url] = best
        
        # Track what was removed
        for score, item in scored[1:]:
            removed.append(item)
            print(f"  Removing: ID {item.get('id')} (score: {score}) - Keeping: ID {best.get('id')} (score: {scored[0][0]})")

# Add items without URLs (can't deduplicate these reliably)
deduplicated.extend(no_url)

print(f"\n=== RESULTS ===")
print(f"Original count: {len(artworks)}")
print(f"Duplicates removed: {len(removed)}")
print(f"Final count: {len(deduplicated)}")

# Save deduplicated data
with open(r'C:\sandbox\esm\artwork_data.json', 'w', encoding='utf-8') as f:
    json.dump(deduplicated, f, indent=4, ensure_ascii=False)

print(f"\nSaved deduplicated data to artwork_data.json")

# Save removed items for reference
if removed:
    with open(r'C:\sandbox\esm\removed_duplicates.json', 'w', encoding='utf-8') as f:
        json.dump(removed, f, indent=4, ensure_ascii=False)
    print(f"Saved {len(removed)} removed items to removed_duplicates.json")
