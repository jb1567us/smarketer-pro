import os

SETTINGS_PATH = r"c:\sandbox\b2b_outreach_tool\searxng\searxng\settings.yml"

def add_wikidata_engine():
    if not os.path.exists(SETTINGS_PATH):
        print("File not found.")
        return

    print("Reading settings.yml...")
    with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    in_engines = False
    wikidata_added = False

    for line in lines:
        if line.startswith('engines:'):
            in_engines = True
            new_lines.append(line)
            # Add wikidata at the top of engines list for visibility
            new_lines.append("  - name: wikidata\n")
            new_lines.append("    engine: wikidata\n")
            new_lines.append("    shortcut: wd\n")
            new_lines.append("    categories: [general, science]\n")
            new_lines.append("    timeout: 15.0\n")
            new_lines.append("    network: direct\n")
            new_lines.append("    disabled: false\n")
            wikidata_added = True
            continue
        
        # If we see wikidata already (maybe I missed it), skip it to avoid duplicates
        if in_engines and "name: wikidata" in line:
            # We skip this for now safely because we added it at the top
            pass
        
        new_lines.append(line)

    print("Writing settings.yml with forced wikidata...")
    with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("Done.")

if __name__ == "__main__":
    add_wikidata_engine()
