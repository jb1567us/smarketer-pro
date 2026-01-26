import os
import re

BAK_PATH = r"c:\sandbox\b2b_outreach_tool\searxng\searxng\settings.yml.pre_deepclean.bak"
DEST_PATH = r"c:\sandbox\b2b_outreach_tool\searxng\searxng\settings.yml"

def regex_surgical_clean():
    if not os.path.exists(BAK_PATH):
        print("Backup file not found.")
        return

    print("Reading settings.yml.pre_deepclean.bak...")
    with open(BAK_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # Define the clean outgoing block (root level)
    clean_outgoing = """outgoing:
  request_timeout: 30.0
  max_request_timeout: 45.0
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

    # USE REGEX to find 'outgoing:' at the start of a line and replace until the next root key
    # A root key is a word at the start of a line (0 indentation) followed by a colon.
    # Ex: brand:, search:, server:, ui:, plugins:, engines:
    
    # Pattern: 'outgoing:' at start of line, followed by anything that has leading whitespace, 
    # until we hit another word at the start of a line.
    
    pattern = re.compile(r'^outgoing:.*?^(?=[a-z])', re.MULTILINE | re.DOTALL)
    
    if pattern.search(content):
        print("Found outgoing block. Replacing...")
        new_content = pattern.sub(clean_outgoing + "\n", content)
    else:
        print("Could not find outgoing block via regex. Falling back to append.")
        new_content = content + "\n\n" + clean_outgoing

    # Ensure no duplicates if multiple outgoing blocks exist
    # (Though regex should find the first one and the others weren't in this version)

    print(f"Writing clean config to {DEST_PATH}...")
    with open(DEST_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("Done.")

if __name__ == "__main__":
    regex_surgical_clean()
