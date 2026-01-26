import re
import os

SETTINGS_PATH = r"c:\sandbox\b2b_outreach_tool\searxng\searxng\settings.yml"

def rescue_settings():
    if not os.path.exists(SETTINGS_PATH):
        print("File not found.")
        return

    print("Reading settings.yml...")
    with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    skip_mode = False
    
    # We want to replace the entire 'outgoing:' block or at least the 'proxies:' part of it.
    # Given the mess, let's find 'outgoing:' and rewrite it completely, 
    # skipping everything until the next major section (root level key).
    
    # Actually, 'outgoing' is a root key. 
    # So we can skip from 'outgoing:' until the next line that starts with alphanumeric at col 0.
    
    outgoing_inserted = False

    for line in lines:
        if line.startswith('outgoing:'):
            skip_mode = True
            continue
        
        if skip_mode:
            # If we hit another root key (no indentation), stop skipping
            if re.match(r'^[a-z]', line): 
                skip_mode = False
                # Insert our fresh outgoing block before this new key
                if not outgoing_inserted:
                    new_lines.append("outgoing:\n")
                    new_lines.append("  request_timeout: 20.0\n")
                    new_lines.append("  max_request_timeout: 20.0\n")
                    new_lines.append("  pool_connections: 100\n")
                    new_lines.append("  pool_maxsize: 100\n")
                    new_lines.append("  enable_http2: true\n")
                    new_lines.append("  proxies:\n")
                    new_lines.append("    all://: []\n") # Explicit empty list
                    outgoing_inserted = True
                new_lines.append(line)
            else:
                # Still inside outgoing (or garbage), skip it
                pass
        else:
            # Fix specific line corruption if it exists elsewhere
            if "yacy: {}    all://: []" in line:
                line = line.replace("    all://: []", "")
            new_lines.append(line)

    # In case outgoing was at the very end and we never hit a new key
    if skip_mode and not outgoing_inserted:
         new_lines.append("outgoing:\n")
         new_lines.append("  request_timeout: 20.0\n")
         new_lines.append("  max_request_timeout: 20.0\n")
         new_lines.append("  proxies:\n")
         new_lines.append("    all://: []\n")

    print("Writing sanitized settings.yml...")
    with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

    print("Rescue complete.")

if __name__ == "__main__":
    rescue_settings()
