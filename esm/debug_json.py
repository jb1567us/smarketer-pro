import json
import os
import sys

file_path = r'c:\sandbox\esm\artwork_data.json'

if not os.path.exists(file_path):
    print("File not found")
    sys.exit(1)

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        data = json.loads(content)
        
    print("JSON is valid.")
    print(f"Count: {len(data)}")
    
    for item in data:
        title = item.get('title', 'NO TITLE')
        desc = item.get('description', '')
        if '{' in desc or 'function' in desc or '<?php' in desc:
            print(f"WARNING: Suspicious description in '{title}'")
            print(f"  Desc start: {desc[:100]}...")
            
except json.JSONDecodeError as e:
    print(f"JSON Error: {e}")
except Exception as e:
    print(f"Error: {e}")
