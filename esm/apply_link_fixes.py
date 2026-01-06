import json

def apply_fixes():
    path = r"c:\sandbox\esm\artwork_data.json"
    
    # Correct URLs from reference list
    corrections = {
        "Waves": "https://www.saatchiart.com/art/Painting-Waves/1295487/6364287/view",
        "Blue Glacier": "https://www.saatchiart.com/art/Painting-Blue-Glacier/1295487/6446603/view"
    }

    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    updated = False
    for item in data:
        title = item.get("title", "")
        if title in corrections:
            old_url = item.get("saatchi_url")
            new_url = corrections[title]
            if old_url != new_url:
                print(f"Updating '{title}':\n  OLD: {old_url}\n  NEW: {new_url}")
                item["saatchi_url"] = new_url
                updated = True
    
    if updated:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print("Successfully updated artwork_data.json")
    else:
        print("No updates needed (already correct or titles not matched).")

if __name__ == "__main__":
    apply_fixes()
