import json

# Load collections and artwork data
with open(r'C:\sandbox\esm\collections_data.json', 'r', encoding='utf-8') as f:
    collections = json.load(f)

with open(r'C:\sandbox\esm\artwork_data.json', 'r', encoding='utf-8') as f:
    artworks_list = json.load(f)

# Create lookup by saatchi_url
artworks_by_url = {a['saatchi_url']: a for a in artworks_list if a.get('saatchi_url')}

# Check each collection
total_in_collections = 0
missing_links = 0
missing_pages = []

for coll_key, coll_data in collections.items():
    print(f"\n{coll_data['title']}:")
    print(f"  Total artworks: {len(coll_data['artworks'])}")
    
    total_in_collections += len(coll_data['artworks'])
    
    no_link = 0
    no_wordpress = 0
    
    for artwork in coll_data['artworks']:
        has_link = artwork.get('link')
        has_wordpress_link = has_link and 'elliotspencermorgan.com' in has_link
        
        if not has_link:
            no_link += 1
            missing_links += 1
            missing_pages.append({
                'title': artwork.get('title'),
                'saatchi_url': artwork.get('saatchi_url'),
                'collection': coll_data['title']
            })
        elif not has_wordpress_link:
            no_wordpress += 1
            missing_links += 1
            missing_pages.append({
                'title': artwork.get('title'),
                'link': has_link,
                'collection': coll_data['title']
            })
    
    if no_link or no_wordpress:
        print(f"  ⚠️ Missing: {no_link} without link, {no_wordpress} with non-WP link")

print(f"\n=== SUMMARY ===")
print(f"Total artworks in collections: {total_in_collections}")
print(f"Artworks missing WordPress links: {missing_links}")

if missing_pages:
    print(f"\nMissing pages (first 20):")
    for item in missing_pages[:20]:
        print(f"  - {item['title']} ({item.get('collection', 'Unknown')})")

print(f"\nThese artworks need WordPress pages created!")
