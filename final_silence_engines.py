import os

SETTINGS_PATH = r"c:\sandbox\b2b_outreach_tool\searxng\searxng\settings.yml"

def final_silence_engines():
    if not os.path.exists(SETTINGS_PATH):
        print("File not found.")
        return

    print(f"Reading {SETTINGS_PATH}...")
    with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    engines_found = False
    
    for line in lines:
        new_lines.append(line)
        if line.strip().startswith('engines:') and not engines_found:
            engines_found = True
            # Add our disabled blocks right at the top
            new_lines.append("  - name: wikidata\n")
            new_lines.append("    engine: wikidata\n")
            new_lines.append("    disabled: true\n")
            new_lines.append("\n")
            new_lines.append("  - name: radio browser\n")
            new_lines.append("    engine: radio_browser\n")
            new_lines.append("    disabled: true\n")
            new_lines.append("\n")
            new_lines.append("  - name: torch\n")
            new_lines.append("    engine: torch\n")
            new_lines.append("    disabled: true\n")
            new_lines.append("\n")

    print(f"Writing updated config to {SETTINGS_PATH}...")
    with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("Done.")

if __name__ == "__main__":
    final_silence_engines()
