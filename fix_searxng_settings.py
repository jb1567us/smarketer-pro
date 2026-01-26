
import yaml
import os
import re

SETTINGS_PATH = r"c:\sandbox\b2b_outreach_tool\searxng\searxng\settings.yml"

def fix_settings():
    if not os.path.exists(SETTINGS_PATH):
        print(f"File not found: {SETTINGS_PATH}")
        return

    with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    unique_proxies = set()
    cleaned_lines = []
    
    # 1. First pass: Collect proxies and fix syntax errors
    for line in lines:
        stripped = line.strip()
        
        # Regex for proxy:  - http://...
        # We capture generic http/https proxies.
        m = re.search(r'^\s*-\s*(https?://[a-zA-Z0-9\.:]+)', line)
        if m:
            unique_proxies.add(m.group(1))
            # We will NOT add this line to cleaned_lines (we strip it out)
            continue
            
        # Fix corrupted lines
        if "ipv6: ::    all://:" in line:
            parts = line.split("    all://:")
            cleaned_lines.append(parts[0] + "\n")
            continue
            
        if "direct: {}    all://:" in line:
             parts = line.split("    all://:")
             cleaned_lines.append(parts[0] + "\n")
             continue
             
        # Skip stray `all://:` keys entirely
        if stripped.startswith("all://:") or stripped.startswith("'all://':"):
            continue
            
        # If line contains `all://:` but is not a comment, and we haven't handled it
        if "all://:" in line and not stripped.startswith("#"):
             # It might be `    all://:` indented.
             # We skip it.
             continue
             
        cleaned_lines.append(line)

    print(f"Found {len(unique_proxies)} unique proxies.")
    
    # 2. Second pass: Inject the proxy list at the right place.
    # We look for "proxies:" under "outgoing:".
    
    final_output = []
    found_proxies_section = False
    
    for line in cleaned_lines:
        stripped = line.strip()
        
        if stripped == "proxies:" and not found_proxies_section:
            final_output.append(line)
            found_proxies_section = True
            
            # Inject consolidated list
            final_output.append("    all://:\n")
            # Sort proxies for determinism
            for p in sorted(list(unique_proxies)):
                final_output.append(f"      - {p}\n")
        else:
            final_output.append(line)
            
    # Write to file
    with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
        f.writelines(final_output)
    
    print("Fixed settings.yml with aggressive cleaning.")

if __name__ == "__main__":
    fix_settings()
