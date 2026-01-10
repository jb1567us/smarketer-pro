
targets = ["red planet", "in the dark", "warm glacier", "sunset glacier"]

try:
    with open(r'c:\sandbox\esm\artwork_data.json', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print("Searching raw lines...")
    for i, line in enumerate(lines):
        line_lower = line.lower()
        for t in targets:
            if t in line_lower:
                print(f"MATCH: '{t}' at line {i+1}: {line.strip()}")

except Exception as e:
    print(f"Error: {e}")
