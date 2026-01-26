import os

SETTINGS_PATH = r"c:\sandbox\b2b_outreach_tool\searxng\searxng\settings.yml"

def surgical_deep_clean():
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
        if line.startswith('outgoing:'):
            in_outgoing = True
            continue 
        
        if in_outgoing:
            # Look for next root key (starts at col 0, not a space)
            if line and line[0].isalnum() and not line.startswith(' '):
                in_outgoing = False
                # Insert our fresh, clean outgoing block
                if not outgoing_replaced:
                    new_lines.append("outgoing:\n")
                    new_lines.append("  request_timeout: 20.0\n")
                    new_lines.append("  max_request_timeout: 20.0\n")
                    new_lines.append("  pool_connections: 100\n")
                    new_lines.append("  pool_maxsize: 100\n")
                    new_lines.append("  enable_http2: true\n")
                    new_lines.append("  networks:\n")
                    new_lines.append("    direct:\n")
                    new_lines.append("      local_addresses:\n")
                    new_lines.append("        - 0.0.0.0\n")
                    new_lines.append("    yandex: {}\n")
                    new_lines.append("    brave: {}\n")
                    new_lines.append("    yacy: {}\n")
                    new_lines.append("    seekr: {}\n")
                    # NO PROXIES HERE - Direct only
                    new_lines.append("\n")
                    outgoing_replaced = True
                new_lines.append(line)
            else:
                # Inside old outgoing, skip everything
                pass
        else:
            new_lines.append(line)

    if in_outgoing and not outgoing_replaced:
        new_lines.append("outgoing:\n")
        new_lines.append("  request_timeout: 20.0\n")
        new_lines.append("  max_request_timeout: 20.0\n")
        new_lines.append("  pool_connections: 100\n")
        new_lines.append("  pool_maxsize: 100\n")
        new_lines.append("  enable_http2: true\n")
        new_lines.append("  networks:\n")
        new_lines.append("    direct:\n")
        new_lines.append("      local_addresses:\n")
        new_lines.append("        - 0.0.0.0\n")
        new_lines.append("    yandex: {}\n")
        new_lines.append("    brave: {}\n")
        new_lines.append("    yacy: {}\n")
        new_lines.append("    seekr: {}\n")
        outgoing_replaced = True

    print("Writing surgically cleaned settings.yml...")
    with open(SETTINGS_PATH, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("Done.")

if __name__ == "__main__":
    surgical_deep_clean()
