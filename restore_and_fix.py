import os
import re

BAK_PATH = r"c:\sandbox\b2b_outreach_tool\searxng\searxng\settings.yml.bak"
TARGET_PATH = r"c:\sandbox\b2b_outreach_tool\searxng\searxng\settings.yml"

def restore_and_fix_v2():
    if not os.path.exists(BAK_PATH):
        print(f"Backup not found: {BAK_PATH}")
        return

    print(f"Reading from backup {BAK_PATH}...")
    with open(BAK_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    skip_proxies = False
    outgoing_found = False

    for line in lines:
        stripped = line.strip()
        
        # 1. Handle outgoing section
        if line.startswith('outgoing:'):
            outgoing_found = True
            new_lines.append(line)
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
            # NO PROXIES HERE
            continue

        if outgoing_found:
            # Skip proxy definitions until the next root key
            if line.startswith('  proxies:'):
                skip_proxies = True
                continue
            
            if skip_proxies:
                if line and not line.startswith(' '):
                    skip_proxies = False
                    outgoing_found = False
                    new_lines.append(line)
                continue
            
            # Skip other keys we've already injected
            if stripped.startswith('request_timeout:') or \
               stripped.startswith('max_request_timeout:') or \
               stripped.startswith('pool_connections:') or \
               stripped.startswith('pool_maxsize:') or \
               stripped.startswith('enable_http2:') or \
               stripped.startswith('networks:'):
                continue
                
            if line and not line.startswith(' '):
                outgoing_found = False
                new_lines.append(line)
        else:
            new_lines.append(line)

    print(f"Writing fixed settings to {TARGET_PATH}...")
    with open(TARGET_PATH, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print("Done.")

if __name__ == "__main__":
    restore_and_fix_v2()
