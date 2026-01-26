
import re

file_path = 'c:\\sandbox\\b2b_outreach_tool\\searxng\\searxng\\settings.yml'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Helper function to disable an engine if not already disabled
def disable_engine(content, engine_name):
    # This regex finds the engine name and captures the block until the next "  - name:" or end of engines block
    # It's a bit of a heuristic.
    # A safer way allows for multiple matches and checks each.
    
    # We want to match:
    #   - name: engine_name
    #     ...
    #     (no disabled: true)
    #
    # We will use a callback to inspect each match.
    
    pattern = re.compile(r'((\s*-\s+name:\s+' + re.escape(engine_name) + r')\s*\n(?:(?!\s*-\s+name:).)*?)(?=\n\s*-\s+name:|\Z)', re.DOTALL)
    
    def replace_callback(match):
        block = match.group(1)
        if 'disabled: true' in block:
            return block # Already disabled, leave it
        else:
            print(f"Disabling active '{engine_name}' block...")
            # Insert disabled: true after the name line
            return re.sub(r'(name:\s+' + re.escape(engine_name) + r')', r'\1\n    disabled: true', block, count=1)

    new_content = pattern.sub(replace_callback, content)
    return new_content

content = disable_engine(content, 'radio browser')
content = disable_engine(content, 'torch')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updates complete.")
