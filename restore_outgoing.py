import os

SETTINGS_PATH = r"c:\sandbox\b2b_outreach_tool\searxng\searxng\settings.yml"

def restore_outgoing():
    if not os.path.exists(SETTINGS_PATH):
        print("File not found.")
        return

    print("Reading settings.yml...")
    with open(SETTINGS_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Check if outgoing exists
    has_outgoing = any(line.strip().startswith('outgoing:') for line in lines)
    
    if has_outgoing:
        print("Outgoing section already exists. Doing nothing.")
        return

    print("Appending outgoing section...")
    
    # We'll just append it to the end.
    with open(SETTINGS_PATH, 'a', encoding='utf-8') as f:
        f.write("\n")
        f.write("outgoing:\n")
        f.write("  request_timeout: 20.0\n")
        f.write("  max_request_timeout: 20.0\n")
        f.write("  pool_connections: 100\n")
        f.write("  pool_maxsize: 100\n")
        f.write("  enable_http2: true\n")
        f.write("  proxies:\n")
        f.write("    all://: []\n")

    print("Restored outgoing section.")

if __name__ == "__main__":
    restore_outgoing()
