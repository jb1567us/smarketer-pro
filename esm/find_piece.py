import json

def find_artwork():
    path = r"c:\sandbox\esm\artwork_data.json"
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for i, line in enumerate(lines):
        if "Pieces of Red" in line:
            print(f"Found at line {i+1}: {line.strip()}")
            # Print surrounding lines
            start = max(0, i-5)
            end = min(len(lines), i+25)
            for j in range(start, end):
                print(f"{j+1}: {lines[j].rstrip()}")
            return

    print("Not found")

if __name__ == "__main__":
    find_artwork()
