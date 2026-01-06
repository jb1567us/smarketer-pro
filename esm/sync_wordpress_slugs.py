import json

# Load WordPress pages data
with open(r'C:\sandbox\esm\wordpress_pages_current.json', 'r', encoding='utf-8') as f:
    wp_pages = json.load(f)

print(f"Loaded {len(wp_pages)} WordPress pages")

# Load artwork data
with open(r'C:\sandbox\esm\artwork_data.json', 'r', encoding='utf-8') as f:
    artworks = json.load(f)

print(f"Loaded {len(artworks)} artworks")

# Create lookup by title (normalized)
def normalize_title(title):
    """Normalize title for matching"""
    return title.lower().strip().replace('painting', '').replace('sculpture', '').replace('collage', '').strip()

wp_by_title = {}
for page in wp_pages:
    norm_title = normalize_title(page['title'])
    wp_by_title[norm_title] = page

# Update artworks with WordPress data
updated = 0
not_found = []

for artwork in artworks:
    title = artwork.get('title', '')
    norm_title = normalize_title(title)
    
    if norm_title in wp_by_title:
        wp_page = wp_by_title[norm_title]
        
        # Update with WordPress data
        artwork['link'] = wp_page['link']
        artwork['slug'] = wp_page['slug']
        artwork['wordpress_id'] = wp_page['id']
        updated += 1
    else:
        not_found.append(title)

print(f"\n=== RESULTS ===")
print(f"Updated: {updated} artworks")
print(f"Not found: {len(not_found)}")

if not_found and len(not_found) <= 10:
    print("\nNot found in WordPress:")
    for title in not_found:
        print(f"  - {title}")

# Save updated artwork data
with open(r'C:\sandbox\esm\artwork_data.json', 'w', encoding='utf-8') as f:
    json.dump(artworks, f, indent=4, ensure_ascii=False)

print(f"\nSaved updated artwork_data.json")
