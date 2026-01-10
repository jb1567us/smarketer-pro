
import json
import os

file_path = r'c:\sandbox\esm\artwork_data.json'
ids_to_remove = [1704, 161, 241, 242]

# 1. Read raw content
with open(file_path, 'r', encoding='utf-8') as f:
    raw_content = f.read()

# 2. Fix syntax error manually because JSON load will fail
# The error identified is a missing closing brace and comma before new objects start around line 3989
# We look for the "Pieces of Red Collage" entry and specific detected_colors end
# Pattern matching specific context seen in view_file
bad_sequence = '        ],\n        {\n            "id": 9901,'
fixed_sequence = '        ]\n    },\n    {\n        "id": 9901,'

if bad_sequence in raw_content:
    print("Found syntax error pattern. Fixing...")
    fixed_content = raw_content.replace(bad_sequence, fixed_sequence)
else:
    print("Syntax error pattern not found exact match. Proceeding with caution.")
    fixed_content = raw_content

# 3. Parse JSON
try:
    data = json.loads(fixed_content)
    print(f"Successfully loaded JSON. Total items: {len(data)}")
except json.JSONDecodeError as e:
    print(f"Failed to decode JSON: {e}")
    # Fallback: simple text removal if strictly necessary, but better to fix structure
    exit(1)

# 4. Filter artworks
new_data = [item for item in data if item.get('id') not in ids_to_remove]

print(f"Removed {len(data) - len(new_data)} items.")

# 5. Write back
with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(new_data, f, indent=4)

print("Done.")
