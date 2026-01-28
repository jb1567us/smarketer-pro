import re
import os

SETTINGS_PATH = r"c:\sandbox\b2b_outreach_tool\searxng\searxng\settings.yml"

def clean_settings():
    if not os.path.exists(SETTINGS_PATH):
        print(f"Error: {SETTINGS_PATH} not found.")
        return

    with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    print(f"Original size: {len(content)} bytes")

    # Split into parts to isolate the outgoing section
    if "outgoing:" not in content:
        print("Error: 'outgoing:' section not found.")
        return

    parts = content.split("outgoing:", 1)
    pre_outgoing = parts[0]
    post_outgoing = parts[1]

    # Regex to find the proxies block. 
    # It looks for 'proxies:', then indented lines following it.
    # We want to remove ALL occurrences of proxies blocks in the post_outgoing part
    # because the bug caused them to be appended multiple times.
    
    # This regex matches "  proxies:" followed by any number of lines that are indented 
    # (start with 4 spaces) or blank lines, until it hits something that isn't.
    # We'll valid yaml structure assumptions here: keys in this file seem to be 2-space indented.
    # "  proxies:" is 2 spaces. content inside is 4 spaces.
    
    regex_proxies = r"(\n  proxies:\n(?:    .*\n)*)"
    
    # Remove all matches
    cleaned_post_outgoing = re.sub(regex_proxies, "", post_outgoing, flags=re.MULTILINE)
    
    # Now we have a clean post_outgoing without ANY proxies.
    # We should add back a clean, empty or placeholder proxies block if needed, 
    # but the ProxyManager is supposed to add it. 
    # Let's add a disabled placeholder to be safe and valid YAML.
    
    placeholder = "\n  proxies:\n    # Proxies disabled (cleaned)\n"
    
    final_content = pre_outgoing + "outgoing:" + placeholder + cleaned_post_outgoing.lstrip()
    
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        f.write(final_content)

    print(f"Cleaned size: {len(final_content)} bytes")
    print("Settings file cleaned.")

if __name__ == "__main__":
    clean_settings()
