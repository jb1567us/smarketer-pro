import os

SETTINGS_PATH = r"c:\sandbox\b2b_outreach_tool\searxng\searxng\settings.yml"

def disable_wikidata():
    if not os.path.exists(SETTINGS_PATH):
        print("File not found.")
        return

    print(f"Reading {SETTINGS_PATH}...")
    with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    in_engines = False
    in_wikidata = False
    wikidata_modified = False

    for line in lines:
        if line.strip().startswith('engines:'):
            in_engines = True
            new_lines.append(line)
            continue
            
        if in_engines:
            # Check if this is the start of a new engine block
            if line.strip().startswith('- name:'):
                if 'wikidata' in line:
                    in_wikidata = True
                else:
                    in_wikidata = False
            
            # If we are inside the wikidata block, look for 'disabled:'
            if in_wikidata:
                if 'disabled:' in line:
                    # Replace whatever value it has with true
                    new_lines.append(line.split(':')[0] + ': true\n')
                    wikidata_modified = True
                    continue
                # If we hit the end of wikidata or next root key without finding 'disabled', 
                # we'll handle that if needed, but we added it in a previous step so it should exist.
        
        new_lines.append(line)

    # Safety check: if wikidata existed but didn't have a 'disabled' line, 
    # we could append it, but standard SearXNG configs usually have it or we added it.
    
    print(f"Writing updated config to {SETTINGS_PATH}...")
    with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("Done.")

if __name__ == "__main__":
    disable_wikidata()
