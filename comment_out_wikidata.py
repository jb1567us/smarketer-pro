
import re

file_path = 'c:\\sandbox\\b2b_outreach_tool\\searxng\\searxng\\settings.yml'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip_mode = False

for line in lines:
    # Check for engine start
    match = re.search(r'^\s*-\s+name:\s+wikidata', line)
    if match:
        skip_mode = True
        print("Found wikidata block, commenting out...")
    
    # If we find the start of the NEXT engine (or end of list), stop skipping/commenting
    # But wait, we just want to comment out THIS block.
    # The next block starts with "- name:" or '#' if we commented it out previously
    if skip_mode:
        # Check if this line is a NEW engine start (that isn't wikidata)
        # Note: we need to careful not to stop on the wikidata line itself
        if not match and re.search(r'^\s*-\s+name:', line) or re.search(r'^\s*#\s*-\s+name:', line):
             # verify it's not the wikidata line we just found
             skip_mode = False
        
    if skip_mode:
        new_lines.append('# ' + line)
    else:
        new_lines.append(line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Commented out wikidata.")
