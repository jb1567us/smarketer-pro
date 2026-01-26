import os

SETTINGS_PATH = r"c:\sandbox\b2b_outreach_tool\searxng\searxng\settings.yml"

def excise_wikidata():
    if not os.path.exists(SETTINGS_PATH):
        print("File not found.")
        return

    print(f"Reading {SETTINGS_PATH}...")
    with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    in_engines = False
    in_wikidata = False
    wikidata_removed_count = 0

    for line in lines:
        stripped = line.strip()
        
        if stripped.startswith('engines:'):
            in_engines = True
            new_lines.append(line)
            continue
            
        if in_engines:
            if stripped.startswith('- name:'):
                if 'wikidata' in stripped.lower():
                    in_wikidata = True
                    wikidata_removed_count += 1
                    continue
                else:
                    in_wikidata = False
            
            if in_wikidata:
                continue
                
        # If we hit another root key
        if line and line[0].isalnum() and not line.startswith(' '):
            in_engines = False
            in_wikidata = False

        new_lines.append(line)

    print(f"Total Wikidata blocks removed: {wikidata_removed_count}")
    print(f"Writing updated config to {SETTINGS_PATH}...")
    with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("Done.")

if __name__ == "__main__":
    excise_wikidata()
