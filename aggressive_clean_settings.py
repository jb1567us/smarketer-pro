import os
import re

SETTINGS_PATH = r"c:\sandbox\b2b_outreach_tool\searxng\searxng\settings.yml"

def aggressive_clean():
    if not os.path.exists(SETTINGS_PATH):
        print("File not found.")
        return

    print("Reading settings.yml...")
    with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # Define the clean outgoing block
    clean_outgoing = """outgoing:
  request_timeout: 20.0
  max_request_timeout: 20.0
  pool_connections: 100
  pool_maxsize: 100
  enable_http2: true
  networks:
    direct:
      local_addresses:
        - 0.0.0.0
    yandex: {}
    brave: {}
    yacy: {}
    seekr: {}
"""

    # We want to find the 'outgoing:' part and everything after it until the next root key.
    # Root keys in this file seem to be: general, brand, search, server, valkey, ui, plugins, checker, categories_as_tabs, engines, doi_resolvers.
    # Looking at the file, 'plugins' comes after 'outgoing'.
    
    # Let's use a more localized replacement first.
    # Find 'outgoing:' and skip until a line that starts with a non-space char or end of file.
    
    lines = content.splitlines()
    new_lines = []
    skipping = False
    outgoing_added = False

    for line in lines:
        if line.startswith('outgoing:'):
            skipping = True
            if not outgoing_added:
                new_lines.append(clean_outgoing)
                outgoing_added = True
            continue
        
        if skipping:
            # Check if this is a new root-level key
            if line and line[0].isalnum() and not line.startswith(' '):
                skipping = False
                new_lines.append(line)
            else:
                # Still in outgoing, skip
                continue
        else:
            new_lines.append(line)

    print("Writing aggressively cleaned settings.yml...")
    with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(new_lines) + '\n')
    
    print("Done.")

if __name__ == "__main__":
    aggressive_clean()
