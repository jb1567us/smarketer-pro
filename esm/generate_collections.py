import json

# Load artwork data
with open(r'C:\sandbox\esm\artwork_data.json', 'r', encoding='utf-8') as f:
    artworks = json.load(f)

# Filter artworks into collections
collections = {
    'gold-collection': {
        'title': 'Gold Collection',
        'slug': 'gold-collection',
        'description': 'Luxurious gold-toned abstract paintings featuring metallic accents and warm, sophisticated palettes. Perfect for adding elegance to modern interiors.',
        'artworks': []
    },
    'blue-turquoise-collection': {
        'title': 'Blue & Turquoise Collection',
        'slug': 'blue-turquoise-collection',
        'description': 'Calming blue and turquoise abstract artworks inspired by water, glaciers, and coastal landscapes. Ideal for creating serene, peaceful spaces.',
        'artworks': []
    },
    'oversized-statement-pieces': {
        'title': 'Oversized Statement Pieces',
        'slug': 'oversized-statement-pieces',
        'description': 'Large-format abstract art (48 inches or larger) designed to make a bold statement. Perfect for spacious walls, lobbies, and designer projects.',
        'artworks': []
    },
    'sculpture-collection': {
        'title': 'Sculpture Collection',
        'slug': 'sculpture-collection',
        'description': 'Contemporary abstract sculptures and three-dimensional wall art. Unique pieces that add depth and dimension to any space.',
        'artworks': []
    },
    'pattern-geometric': {
        'title': 'Pattern & Geometric',
        'slug': 'pattern-geometric',
        'description': 'Abstract artworks featuring geometric patterns, repetition, and structured compositions. Modern pieces for sophisticated, contemporary interiors.',
        'artworks': []
    },
    'minimalist-abstract': {
        'title': 'Minimalist Abstract',
        'slug': 'minimalist-abstract',
        'description': 'Understated and elegant. These minimalist abstract works focus on form, space, and simplicity to create a calming atmosphere.',
        'artworks': []
    },
    'neutral-tones': {
        'title': 'Neutral Tones',
        'slug': 'neutral-tones',
        'description': 'A curated selection of artworks in beige, grey, cream, and earth tones. Versatile pieces that complement any interior design style.',
        'artworks': []
    }
}

# Categorize artworks
for item in artworks:
    title_lower = (item.get('title') or '').lower()
    url_lower = (item.get('saatchi_url') or '').lower()
    
    # Parse dimensions safely
    try:
        width = float(item.get('width', 0)) if item.get('width') else 0
        height = float(item.get('height', 0)) if item.get('height') else 0
    except (ValueError, TypeError):
        width = 0
        height = 0
    
    # Skip items without proper data
    if not item.get('saatchi_url'):
        continue
    
    # Helpers
    detected_colors = item.get('detected_colors', [])
    styles_lower = (item.get('styles') or '').lower()
    mediums_lower = (item.get('mediumsDetailed') or '').lower()

    # Gold Collection
    # Include if title has keyword OR if Gold/Yellow is detected in image
    if any(keyword in title_lower for keyword in ['gold', 'golden', 'nugget', 'fortune']) or \
       'Gold' in detected_colors or 'Yellow' in detected_colors:
        collections['gold-collection']['artworks'].append(item)
    
    # Blue/Turquoise Collection
    # Include if title has keyword OR if Blue/Turquoise/Navy is detected
    if any(keyword in title_lower for keyword in ['blue', 'turquoise', 'glacier', 'cold', 'storm', 'mesh', 'wave', 'water', 'lake', 'sea']) or \
       'Blue' in detected_colors or 'Turquoise' in detected_colors or 'Navy' in detected_colors:
        collections['blue-turquoise-collection']['artworks'].append(item)
    
    # Oversized (48"+)
    if width >= 48 or height >= 48:
        collections['oversized-statement-pieces']['artworks'].append(item)
    
    # Sculpture
    if 'sculpture' in url_lower or 'floating' in title_lower or 'sculpture' in styles_lower or 'sculpture' in mediums_lower:
        collections['sculpture-collection']['artworks'].append(item)
    
    # Pattern/Geometric
    if any(keyword in title_lower for keyword in ['puzzle', 'microscope', 'pattern', 'geometric', 'grid', 'quilted', 'honeycomb', 'cube', 'structure']) or \
       'geometric' in styles_lower or 'pattern' in styles_lower:
        collections['pattern-geometric']['artworks'].append(item)

    # Minimalist Abstract
    if any(keyword in title_lower for keyword in ['minimal', 'simple', 'white', 'space', 'zen', 'quiet', 'soft']) or \
       'minimalism' in styles_lower or ('White' in detected_colors and len(detected_colors) <= 3):
        collections['minimalist-abstract']['artworks'].append(item)

    # Neutral Tones
    if any(keyword in title_lower for keyword in ['neutral', 'beige', 'cream', 'sand', 'earth', 'stone', 'grey', 'gray', 'bone']) or \
       'Beige' in detected_colors or 'Grey' in detected_colors or 'Brown' in detected_colors or 'Silver' in detected_colors:
        collections['neutral-tones']['artworks'].append(item)

# Report
print("Collection Summary:")
for key, col in collections.items():
    print(f"  {col['title']}: {len(col['artworks'])} artworks")

# Save to file
with open(r'C:\sandbox\esm\collections_data.json', 'w', encoding='utf-8') as f:
    json.dump(collections, f, indent=2, ensure_ascii=False)

print(f"\nSaved to collections_data.json")
