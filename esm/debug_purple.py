import json

with open(r'c:\sandbox\esm\artwork_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

found = False
for item in data:
    if 'Purple 1' in item.get('title', ''):
        found = True
        desc = item.get('description', '')
        print(f"Title: {item['title']}")
        print(f"Description length: {len(desc)}")
        print(f"Description content: {desc}")
        print(f"Description repr: {repr(desc)}")
        
        # Check for weird stuff
        if '{' in desc or '}' in desc:
            print("WARNING: Braces in description")
        if '<' in desc:
            print("WARNING: HTML tag start in description")

if not found:
    print("Purple 1 not found")
