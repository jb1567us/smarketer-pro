import os

SETTINGS_PATH = r"c:\sandbox\b2b_outreach_tool\searxng\searxng\settings.yml"

def final_silence_fix():
    print(f"Applying final silence fix to {SETTINGS_PATH}...")
    
    with open(SETTINGS_PATH, 'rb') as f:
        content = f.read().decode('utf-8', errors='ignore')

    lines = content.splitlines()
    new_lines = []
    
    deleted_engines = ['wikidata', 'radio browser', 'torch']
    
    in_engines = False
    skip_mode = False
    
    for line in lines:
        stripped = line.strip()
        
        if stripped.startswith('engines:'):
            in_engines = True
            new_lines.append(line)
            # Add our clean disabled blocks right at the top
            new_lines.append("  - name: wikidata")
            new_lines.append("    engine: wikidata")
            new_lines.append("    shortcut: wd_disabled")
            new_lines.append("    disabled: true")
            new_lines.append("")
            new_lines.append("  - name: radio browser")
            new_lines.append("    engine: radio_browser")
            new_lines.append("    shortcut: rb_disabled")
            new_lines.append("    disabled: true")
            new_lines.append("")
            new_lines.append("  - name: torch")
            new_lines.append("    engine: torch")
            new_lines.append("    shortcut: tr_disabled")
            new_lines.append("    disabled: true")
            new_lines.append("")
            continue
            
        if in_engines:
            if stripped.startswith('- name:'):
                current_name = stripped.replace('- name:', '').strip().lower()
                if current_name in deleted_engines:
                    skip_mode = True
                    continue
                else:
                    skip_mode = False
            
            if skip_mode:
                continue
                
        # If we hit another root key
        if line and line[0].isalnum() and not line.startswith(' '):
            in_engines = False
            skip_mode = False

        new_lines.append(line)

    with open(SETTINGS_PATH, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(new_lines))
    
    print("Done.")

if __name__ == "__main__":
    final_silence_fix()
