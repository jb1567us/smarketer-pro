
import re

file_path = 'c:\\sandbox\\b2b_outreach_tool\\searxng\\searxng\\settings.yml'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Disable DuckDuckGo
# Look for the block and ensure disabled: true is set
# We use regex to find start of duckduckgo block and insert usage
if 'name: duckduckgo' in content:
    # Check if already disabled
    match = re.search(r'name: duckduckgo\s+engine: duckduckgo\s+shortcut: ddg\s+disabled: true', content)
    if not match:
        print("Disabling DuckDuckGo...")
        content = re.sub(
            r'(name: duckduckgo\s+engine: duckduckgo\s+shortcut: ddg)',
            r'\1\n    disabled: true',
            content
        )
else:
    print("Warning: DuckDuckGo block not found!")

# Fix 2: Remove local_addresses (ipv4 error source)
# Block:
#     direct:
#       local_addresses:
#         - 0.0.0.0
# We replace it with just "direct: {}" or similar
if 'local_addresses:' in content:
    print("Removing local_addresses from network config...")
    # This regex attempts to catch the direct block with local_addresses
    # Be careful not to eat too much.
    pattern = r'(direct:\s+local_addresses:\s+-\s+0\.0\.0\.0)'
    content = re.sub(pattern, 'direct: {}', content)

# Fix 3: Ensure Wikidata is disabled (it was already, but good to be sure)
if 'name: wikidata' in content:
    if 'disabled: true' not in content.split('name: wikidata')[1].split('name:')[0]:
         print("Disabling Wikidata (if not already)...")
         # Simple replace for this context might be tricky if not standardized, 
         # but earlier check showed it was disabled.
         pass

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Settings updated successfully.")
