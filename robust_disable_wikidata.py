import os

SETTINGS_PATH = r"c:\sandbox\b2b_outreach_tool\searxng\searxng\settings.yml"

def robust_disable_wikidata():
    if not os.path.exists(SETTINGS_PATH):
        print("File not found.")
        return

    print(f"Reading {SETTINGS_PATH}...")
    with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    in_engines = False
    in_wikidata = False
    wikidata_found = False
    disabled_added = False

    for line in lines:
        if line.strip().startswith('engines:'):
            in_engines = True
            new_lines.append(line)
            continue
            
        if in_engines:
            # Check if this is the start of a new engine block
            if line.strip().startswith('- name:'):
                if 'wikidata' in line.lower():
                    in_wikidata = True
                    wikidata_found = True
                    disabled_added = False
                elif in_wikidata:
                    # Closing previous wikidata block
                    if not disabled_added:
                        new_lines.append("    disabled: true\n")
                    in_wikidata = False
            
            # If we are inside the wikidata block, check if disabled exists
            if in_wikidata:
                if 'disabled:' in line:
                    new_lines.append(line.split(':')[0] + ': true\n')
                    disabled_added = True
                    continue
        
        # If we hit another root key, close wikidata
        if line and line[0].isalnum() and not line.startswith(' '):
             if in_wikidata and not disabled_added:
                 new_lines.append("    disabled: true\n")
             in_wikidata = False
             in_engines = False

        new_lines.append(line)

    if in_wikidata and not disabled_added:
        new_lines.append("    disabled: true\n")

    print(f"Writing updated config to {SETTINGS_PATH}...")
    with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("Done.")

if __name__ == "__main__":
    robust_disable_wikidata()
