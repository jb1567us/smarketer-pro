import yaml

FILE_PATH = r"c:\sandbox\b2b_outreach_tool\searxng\searxng\settings.yml"

def clean_proxies():
    with open(FILE_PATH, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    in_proxies = False
    skip_until = -1

    for i, line in enumerate(lines):
        line_num = i + 1
        
        if line_num == 244:
            # We are at '  proxies:'
            new_lines.append("  # proxies: removed massive failing list\n")
            in_proxies = True
            continue
        
        if in_proxies:
            # Skip all lines that are indented more than 2 spaces (i.e. under outgoing:)
            # Actually, line 1101 starts with 'plugins:' (no spaces)
            # So we skip until we hit a line that starts with something other than '    '
            if line.startswith('    ') or line.strip() == '':
                 continue
            else:
                 in_proxies = False
        
        new_lines.append(line)

    with open(FILE_PATH, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print(f"Successfully cleaned proxies from {FILE_PATH}")

if __name__ == "__main__":
    clean_proxies()
