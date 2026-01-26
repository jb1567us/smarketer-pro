import os

SETTINGS_PATH = r"c:\sandbox\b2b_outreach_tool\searxng\searxng\settings.yml"

def disable_problematic_engines():
    if not os.path.exists(SETTINGS_PATH):
        print("File not found.")
        return

    print(f"Reading {SETTINGS_PATH}...")
    with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    problematic_engines = ['wikidata', 'radio browser', 'torch']
    new_lines = []
    
    in_engines = False
    current_engine = None
    engine_props = {}

    # To be extremely safe, I'll rebuild the engines list logic.
    # But for settings.yml, let's just do a targeted replacement.
    
    skip_until_next = False
    
    for line in lines:
        stripped = line.strip()
        
        if stripped.startswith('engines:'):
            in_engines = True
            new_lines.append(line)
            continue
            
        if in_engines:
            if stripped.startswith('- name:'):
                current_engine = stripped.replace('- name:', '').strip().lower()
                if current_engine in problematic_engines:
                    # We will output a clean disabled block for this
                    new_lines.append(f"  - name: {current_engine}\n")
                    new_lines.append(f"    engine: {current_engine.replace(' ', '_')}\n")
                    new_lines.append("    disabled: true\n")
                    skip_until_next = True
                    continue
                else:
                    skip_until_next = False
            
            if skip_until_next:
                continue
                
        # If we hit next root key
        if line and line[0].isalnum() and not line.startswith(' '):
            in_engines = False
            skip_until_next = False

        new_lines.append(line)

    print(f"Writing updated config to {SETTINGS_PATH}...")
    with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("Done.")

if __name__ == "__main__":
    disable_problematic_engines()
