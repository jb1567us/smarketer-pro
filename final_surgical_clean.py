import os

BAK_PATH = r"c:\sandbox\b2b_outreach_tool\searxng\searxng\settings.yml.bak"
DEST_PATH = r"c:\sandbox\b2b_outreach_tool\searxng\searxng\settings.yml"

def final_surgical_clean():
    if not os.path.exists(BAK_PATH):
        print("Backup file not found.")
        return

    print("Reading settings.yml.bak...")
    with open(BAK_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Lines are 0-indexed in list, but 1-indexed in my earlier discovery.
    # outgoing: line 226 -> index 225
    # plugins: line 3212 -> index 3211
    
    clean_lines = lines[:225] # up to line 225
    
    clean_outgoing = [
        "outgoing:\n",
        "  request_timeout: 30.0\n",
        "  max_request_timeout: 45.0\n",
        "  pool_connections: 100\n",
        "  pool_maxsize: 100\n",
        "  enable_http2: true\n",
        "  networks:\n",
        "    direct:\n",
        "      local_addresses:\n",
        "        - 0.0.0.0\n",
        "    yandex: {}\n",
        "    brave: {}\n",
        "    yacy: {}\n",
        "    seekr: {}\n"
    ]
    
    clean_lines.extend(clean_outgoing)
    clean_lines.extend(lines[3211:]) # from line 3212 onwards
    
    print(f"Writing clean config to {DEST_PATH}...")
    with open(DEST_PATH, 'w', encoding='utf-8') as f:
        f.writelines(clean_lines)
    
    print("Done.")

if __name__ == "__main__":
    final_surgical_clean()
