import json

art_map = {}

# Mock Data
art_raw = [
    {
        "title": "Unique Piece",
        "slug": "unique-piece",
        "image_url": "http://example.com/unique.jpg",
        "width": "10",
        "height": "10"
    },
    {
        "title": "No Public Shrooms",
        "slug": "no-public-shrooms",
        "image_url": "http://example.com/shrooms1.jpg"
        # No dims
    },
    {
        "title": "No Public Shrooms",
        "slug": "no-public-shrooms",
        "image_url": "http://example.com/shrooms2.jpg",
        "width": "10",
        "height": "14" # Has dims, should replace
    }
]

for a in art_raw:
    if not a.get("image_url"):
        continue
    
    # Check dims
    has_dims = bool(a.get("width") and a.get("height") and a["width"] != "undefined" and a["height"] != "undefined")
    existing = art_map.get(a["image_url"])

    if existing:
        existing_has_dims = bool(existing.get("width") and existing.get("height") and existing["width"] != "undefined" and existing["height"] != "undefined")
        if has_dims and not existing_has_dims:
            art_map[a["image_url"]] = a
    else:
        # Title/Slug Collision Check
        duplicate_found = False
        keys_to_remove = []
        
        for key, val in art_map.items():
            if a.get("slug") and val.get("slug") and a["slug"] == val["slug"]:
                duplicate_found = True
                print(f"Duplicate found for slug: {a['slug']}")
                
                val_has_dims = bool(val.get("width") and val.get("height") and val["width"] != "undefined" and val["height"] != "undefined")
                
                if has_dims and not val_has_dims:
                    print("Replacing entry because new one has dimensions.")
                    keys_to_remove.append(key)
                    # We will set the new one after the loop
                else:
                    print("Keeping existing entry.")
                    # If we found a duplicate and we are NOT replacing it, then we effectively discard 'a' 
                    # unless we want to handle 'duplicateFound' differently. 
                    # In JS logic: duplicateFound = true; break; -> if(!duplicateFound) set... 
                    # So if duplicateFound is true, we ONLY set if we deleted the old one? 
                    # Wait, the JS logic was:
                    # if(replace) { delete; set; } break;
                    # if(!duplicateFound) set;
                    
                    # So in Python:
                    pass 
                break
        
        # Apply deletions
        for k in keys_to_remove:
            del art_map[k]
            art_map[a["image_url"]] = a
            # We explicitly added it here, so we shouldn't add it again below
            duplicate_found = True 

        if not duplicate_found:
             art_map[a["image_url"]] = a

artworks = list(art_map.values())
print(f"Final Artworks Count: {len(artworks)}")
for a in artworks:
    print(f"- {a['title']} ({a['image_url']})")

if len(artworks) == 2:
    print("TEST PASSED")
else:
    print("TEST FAILED")
