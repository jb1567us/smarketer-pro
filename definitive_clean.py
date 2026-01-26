import os

BAK_PATH = r"c:\sandbox\b2b_outreach_tool\searxng\searxng\settings.yml.bak"
DEST_PATH = r"c:\sandbox\b2b_outreach_tool\searxng\searxng\settings.yml"

def definitive_clean():
    print(f"Definitive clean of {DEST_PATH}...")
    
    with open(BAK_PATH, 'rb') as f:
        content = f.read().decode('utf-8', errors='ignore')

    lines = content.splitlines()
    new_lines = []
    
    # We know outgoing starts around line 226 and plugins starts around 3212
    # but let's be smarter.
    
    found_outgoing = False
    finished_outgoing = False
    
    for line in lines:
        if line.strip() == 'outgoing:' and not line.startswith(' '):
            found_outgoing = True
            # Add our clean block
            new_lines.append("outgoing:")
            new_lines.append("  request_timeout: 30.0")
            new_lines.append("  max_request_timeout: 60.0")
            new_lines.append("  pool_connections: 100")
            new_lines.append("  pool_maxsize: 100")
            new_lines.append("  enable_http2: true")
            new_lines.append("  networks:")
            new_lines.append("    direct:")
            new_lines.append("      local_addresses:")
            new_lines.append("        - 0.0.0.0")
            new_lines.append("    yandex: {}")
            new_lines.append("    brave: {}")
            new_lines.append("    yacy: {}")
            new_lines.append("    seekr: {}")
            continue
            
        if found_outgoing and not finished_outgoing:
            # Check if this is the next root key
            if line and line[0].isalnum() and not line.startswith(' '):
                finished_outgoing = True
                new_lines.append(line)
            else:
                # Skip proxy lines
                continue
        else:
            new_lines.append(line)

    with open(DEST_PATH, 'w', encoding='utf-8', newline='\n') as f:
        f.write('\n'.join(new_lines))
    
    print("Done.")

if __name__ == "__main__":
    definitive_clean()
