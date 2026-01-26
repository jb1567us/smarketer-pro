import os

SETTINGS_PATH = r"c:\sandbox\b2b_outreach_tool\searxng\searxng\settings.yml"

def force_clean():
    if not os.path.exists(SETTINGS_PATH):
        print("File not found.")
        return

    print("Reading settings.yml...")
    with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    in_outgoing = False
    outgoing_replaced = False

    for line in lines:
        # Check for start of outgoing
        if line.startswith('outgoing:'):
            in_outgoing = True
            continue # skip this line
        
        # Check for start of plugins (or any other root key following outgoing)
        if in_outgoing:
            if line.startswith('plugins:') or line.startswith('server:') or line.startswith('search:') or line.startswith('general:'):
                in_outgoing = False
                
                # Insert clean outgoing here
                if not outgoing_replaced:
                    new_lines.append("outgoing:\n")
                    new_lines.append("  request_timeout: 20.0\n")
                    new_lines.append("  max_request_timeout: 20.0\n")
                    new_lines.append("  pool_connections: 100\n")
                    new_lines.append("  pool_maxsize: 100\n")
                    new_lines.append("  enable_http2: true\n")
                    new_lines.append("  proxies:\n")
                    new_lines.append("    all://: []\n")
                    new_lines.append("\n")
                    outgoing_replaced = True
                
                new_lines.append(line)
            else:
                # We are inside the old outgoing block, skip it
                pass
        else:
            # Not in outgoing, keep line
            # Clean up potential garbage on other lines just in case
            if "    all://: []" in line:
                line = line.replace("    all://: []", "")
            new_lines.append(line)

    # If outgoing was at the end and we never hit another key
    if in_outgoing and not outgoing_replaced:
        new_lines.append("outgoing:\n")
        new_lines.append("  request_timeout: 20.0\n")
        new_lines.append("  max_request_timeout: 20.0\n")
        new_lines.append("  pool_connections: 100\n")
        new_lines.append("  pool_maxsize: 100\n")
        new_lines.append("  enable_http2: true\n")
        new_lines.append("  proxies:\n")
        new_lines.append("    all://: []\n")
        outgoing_replaced = True

    print("Writing force-cleaned settings.yml...")
    with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("Cleaned.")

if __name__ == "__main__":
    force_clean()
