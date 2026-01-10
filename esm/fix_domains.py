import json

file_path = 'artwork_data.json'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Perform global replacement
# pattern: https://lookoverhere.xyz/esm -> https://elliotspencermorgan.com
new_content = content.replace('https://lookoverhere.xyz/esm', 'https://elliotspencermorgan.com')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Global replacement complete.")
