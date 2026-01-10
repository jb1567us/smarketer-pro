import json
import os
import shutil

def migrate():
    # Paths
    base_dir = r"c:\sandbox\esm"
    json_path = os.path.join(base_dir, "artwork_data.json")
    spec_dir = os.path.join(base_dir, "spec_sheets")

    # Load Data
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Build Map: Title -> Slug
    # Spec sheets are currently "Title_spec.pdf" or "Title%20_spec.pdf"? 
    # Actually locally they are "Title_spec.pdf".
    
    title_to_slug = {}
    for item in data:
        if 'title' in item and 'slug' in item:
            # key: "Self Portrait 1" -> value: "self_portrait_1"
            title_to_slug[item['title'].strip()] = item['slug']

    # Iterate Files
    files = os.listdir(spec_dir)
    renamed_count = 0
    
    print(f"Scanning {len(files)} files in {spec_dir}...")

    for filename in files:
        if not filename.endswith("_spec.pdf"):
            continue
            
        # Current: "Self Portrait 1_spec.pdf"
        # Extract Title: "Self Portrait 1"
        current_title = filename.replace("_spec.pdf", "")
        
        # Determine target
        if current_title in title_to_slug:
            slug = title_to_slug[current_title]
            new_filename = f"{slug}_spec.pdf"
            
            if new_filename != filename:
                old_path = os.path.join(spec_dir, filename)
                new_path = os.path.join(spec_dir, new_filename)
                
                # Check for collision?
                if os.path.exists(new_path):
                     print(f"Skipping {filename} -> {new_filename} (Target exists)")
                else:
                    os.rename(old_path, new_path)
                    print(f"Renamed: '{filename}' -> '{new_filename}'")
                    renamed_count += 1
        else:
            print(f"Warning: No slug found for file '{filename}' (Title: '{current_title}')")

    print(f"Migration Complete. Renamed {renamed_count} files.")

if __name__ == "__main__":
    migrate()
