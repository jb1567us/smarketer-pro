lines = []
with open('src/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Target range: 553 to 645 (1-indexed) -> 552 to 645 (0-indexed slices)
start_idx = 552
end_idx = 645 

new_lines = []
for i, line in enumerate(lines):
    if start_idx <= i < end_idx:
        # Dedent by 4 spaces if possible
        if line.startswith("            "):
            new_lines.append(line[4:])
        elif line.startswith("    ") and line.strip() == "": # Empty indented line
             new_lines.append("\n")
        else:
            # Fallback for less indented lines (shouldn't happen based on analysis, but safe keep)
            new_lines.append(line.lstrip()) 
            # Actually, standard lstrip might be too aggressive if it kills distinct indentation.
            # But here we expect everything to be at least 12 spaces deep.
            # Let's try to just slice 4 char.
            # If line is shorter (empty newline), just append.
            if len(line) > 4:
                 # Check if it really has spaces
                 if line.startswith("    "):
                     new_lines.append(line[4:])
                 else:
                     new_lines.append(line)
            else:
                 new_lines.append(line)
    else:
        new_lines.append(line)

with open('src/app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Fixed indentation.")
