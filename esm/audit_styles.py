import json
from collections import Counter

with open('artwork_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

style_counts = Counter()
pattern_counts = Counter()

for item in data:
    # Check Styles
    styles = item.get('styles', '')
    if styles:
        for s in styles.split(','):
            style_counts[s.strip()] += 1
            
    # Check current tags (which might include patterns)
    # We don't have a separate 'patterns' field usually, they are in styles or tags.
    # Let's just look at styles for now.

print("Top 20 Styles:")
for s, c in style_counts.most_common(20):
    print(f"{s}: {c}")

print("\n----------------\n")
print("Art Deco Check:")
ad_count = style_counts['Art Deco']
print(f"Items tagged Art Deco: {ad_count}")
if ad_count > 0:
    print("Sample titles with Art Deco:")
    ad_items = [i['title'] for i in data if 'Art Deco' in i.get('styles', '')]
    print(ad_items[:5])
