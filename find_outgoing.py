
filename = r"c:\sandbox\b2b_outreach_tool\searxng\searxng\settings.yml"
try:
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
        found = False
        for i, line in enumerate(lines):
            if "outgoing:" in line:
                print(f"[{i+1}] {line.strip()}")
                found = True
                # Print next few lines to see context
                for j in range(1, 15):
                    if i+j < len(lines):
                        print(f"[{i+1+j}] {lines[i+j].rstrip()}")
                break
        
        if not found:
            print("outgoing: not found")

except Exception as e:
    print(f"Error: {e}")
