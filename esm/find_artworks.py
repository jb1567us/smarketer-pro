
import json

try:
    with open(r'c:\sandbox\esm\artwork_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    targets = ["red planet", "in the dark", "warm glacier", "sunset glacier"]
    
    print("Searching for targets...")
    for item in data:
        title = item.get('title', '').lower()
        id_val = item.get('id', 'N/A')
        for t in targets:
            if t in title:
                print(f"MATCH: '{t}' -> ID: {id_val}, Title: {item.get('title')}")

except Exception as e:
    print(f"Error: {e}")
