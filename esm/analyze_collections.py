import json

# Load artwork data
with open(r'C:\sandbox\esm\artwork_data.json', 'r', encoding='utf-8') as f:
    artworks = json.load(f)

print(f"Total artworks: {len(artworks)}\n")

# Analyze by title keywords for color themes
colors = {
    'Blue': 0,
    'Gold': 0,
    'Red': 0,
    'Turquoise': 0,
    'Purple': 0,
    'Silver': 0,
    'Black & White': 0
}

for item in artworks:
    title = item.get('title', '').lower()
    if 'blue' in title or 'glacier' in title or 'cold' in title:
        colors['Blue'] += 1
    if 'gold' in title or 'golden' in title:
        colors['Gold'] += 1
    if 'red' in title or 'planet' in title:
        colors['Red'] += 1
    if 'turquoise' in title:
        colors['Turquoise'] += 1
    if 'purple' in title:
        colors['Purple'] += 1
    if 'silver' in title:
        colors['Silver'] += 1
    if 'caviar' in title or 'sheet music' in title:
        colors['Black & White'] += 1

print("Color Themes:")
for color, count in sorted(colors.items(), key=lambda x: x[1], reverse=True):
    if count > 0:
        print(f"  {color}: {count}")

# Analyze by medium/type
types = {'Painting': 0, 'Sculpture': 0, 'Collage': 0, 'Print': 0}
for item in artworks:
    title = item.get('title', '').lower()
    url = item.get('saatchi_url', '').lower()
    if 'sculpture' in title or 'sculpture' in url:
        types['Sculpture'] += 1
    elif 'collage' in title or 'collage' in url:
        types['Collage'] += 1
    elif 'print' in title or 'printmaking' in url:
        types['Print'] += 1
    else:
        types['Painting'] += 1

print("\nArtwork Types:")
for type_name, count in sorted(types.items(), key=lambda x: x[1], reverse=True):
    print(f"  {type_name}: {count}")
