import json

with open('artwork_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

red_count = 0
red_items = []

for item in data:
    tags = item.get('detected_colors', [])
    if 'Red' in tags or 'red' in tags:
        red_count += 1
        red_items.append(item['title'])
    # Also check manual styles?
    elif 'Red' in item.get('styles', '') or 'Red' in item.get('title', ''):
         # It MIGHT be red, but if detected_colors missed it, that's the issue.
         pass

print(f"Total items with VISUAL 'Red' tag: {red_count}")
print("Sample of Red items:")
for t in red_items[:10]:
    print(f"- {t}")

print("\n-------------------\n")

# Check 'Red Planet' specifically
for item in data:
    if 'Red Planet' in item['title']:
        print(f"DEBUG 'Red Planet': Detected Colors: {item.get('detected_colors')}")
