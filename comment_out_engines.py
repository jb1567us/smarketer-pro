
import re

file_path = 'c:\\sandbox\\b2b_outreach_tool\\searxng\\searxng\\settings.yml'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip_mode = False
current_engine = None

for line in lines:
    # Check for engine start
    # e.g. "  - name: radio browser"
    match = re.match(r'^  - name: (.*)', line)
    if match:
        name = match.group(1).strip()
        if name in ['radio browser', 'torch']:
            skip_mode = True
            current_engine = name
            print(f"Commenting out engine: {name}")
        else:
            skip_mode = False
            current_engine = None

    if skip_mode:
        # If we hit an empty line, we might want to stop skipping, but YAML usually has empty lines between items.
        # But we must stop skipping when we hit the NEXT engine.
        # Wait, the logic above handles the next engine start.
        # But what if the next line is just a comment or blank?
        # We should comment out everything until the next "  - name:" or end of engines section.
        # But "  - name:" check is at the top of the loop.
        # So we just prefix with #
        new_lines.append('# ' + line)
    else:
        new_lines.append(line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Commented out radio browser and torch.")
