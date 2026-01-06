import json
import re

# The user-provided list
user_urls = [
    "https://www.saatchiart.com/art/Painting-Caviar/1295487/12292979/view",
    "https://www.saatchiart.com/art/Painting-Convergence/1295487/8754060/view",
    "https://www.saatchiart.com/art/Painting-Meeting-In-The-Middle/1295487/8754042/view",
    "https://www.saatchiart.com/art/Painting-Finger-Print/1295487/8754025/view",
    "https://www.saatchiart.com/art/Painting-Sheet-Music/1295487/8146759/view",
    "https://www.saatchiart.com/art/Painting-Puzzled/1295487/8146584/view",
    "https://www.saatchiart.com/art/Painting-Heart-Work/1295487/8146572/view",
    "https://www.saatchiart.com/art/Painting-Portal-2/1295487/8146546/view",
    "https://www.saatchiart.com/art/Painting-Portal-1/1295487/8146533/view",
    "https://www.saatchiart.com/art/Painting-Self-Portrait-1/1295487/8125469/view",
    "https://www.saatchiart.com/art/Painting-Morning-Joe/1295487/8125458/view",
    "https://www.saatchiart.com/art/Painting-Unity/1295487/8125409/view",
    "https://www.saatchiart.com/art/Painting-Dog-On-A-Bike/1295487/8125271/view",
    "https://www.saatchiart.com/art/Painting-Water-People/1295487/7363373/view",
    "https://www.saatchiart.com/art/Painting-Towers/1295487/7363345/view",
    "https://www.saatchiart.com/art/Painting-Granular/1295487/7363339/view",
    "https://www.saatchiart.com/art/Painting-Puzzle-2/1295487/7363331/view",
    "https://www.saatchiart.com/art/Painting-Puzzle-1/1295487/7363317/view",
    "https://www.saatchiart.com/art/Painting-Trichome/1295487/7363313/view",
    "https://www.saatchiart.com/art/Painting-Trichomes/1295487/7363299/view",
    "https://www.saatchiart.com/art/Painting-Grill/1295487/6783253/view",
    "https://www.saatchiart.com/art/Painting-Quilted/1295487/6783247/view",
    "https://www.saatchiart.com/art/Painting-Interactions/1295487/6783239/view",
    "https://www.saatchiart.com/art/Painting-Rush/1295487/6783231/view",
    "https://www.saatchiart.com/art/Painting-Yorkie/1295487/6783225/view",
    "https://www.saatchiart.com/art/Painting-Night-Sky/1295487/6783211/view",
    "https://www.saatchiart.com/art/Painting-Bold/1295487/6783203/view",
    "https://www.saatchiart.com/art/Painting-Climbing/1295487/6783197/view",
    "https://www.saatchiart.com/art/Painting-Dance/1295487/6783193/view",
    "https://www.saatchiart.com/art/Painting-Smoke/1295487/6783181/view",
    "https://www.saatchiart.com/art/Painting-Motion/1295487/6783137/view",
    "https://www.saatchiart.com/art/Painting-Listening/1295487/6783125/view",
    "https://www.saatchiart.com/art/Painting-Synapses/1295487/6783101/view",
    "https://www.saatchiart.com/art/Painting-Microscope-7/1295487/6782897/view",
    "https://www.saatchiart.com/art/Painting-Microscope-6/1295487/6782859/view",
    "https://www.saatchiart.com/art/Painting-Microscope-5/1295487/6782839/view",
    "https://www.saatchiart.com/art/Painting-Microscope-4/1295487/6782817/view",
    "https://www.saatchiart.com/art/Painting-Microscope-3/1295487/6782785/view",
    "https://www.saatchiart.com/art/Painting-Microscope-2/1295487/6782755/view",
    "https://www.saatchiart.com/art/Painting-Microscope-1/1295487/6782739/view",
    "https://www.saatchiart.com/art/Sculpture-Floating-6-Rabbit/1295487/6627463/view",
    "https://www.saatchiart.com/art/Sculpture-Floating-5-Moth/1295487/6627457/view",
    "https://www.saatchiart.com/art/Sculpture-Floating-4-Vines/1295487/6627447/view",
    "https://www.saatchiart.com/art/Sculpture-Floating-3-Tree/1295487/6627443/view",
    "https://www.saatchiart.com/art/Sculpture-Floating-2-Butterfly/1295487/6627437/view",
    "https://www.saatchiart.com/art/Sculpture-Floating-1-Cicada/1295487/6627409/view",
    "https://www.saatchiart.com/art/Collage-Purple-Night-Mulch-Series/1295487/6583797/view",
    "https://www.saatchiart.com/art/Collage-City-At-Night-Mulch-Series/1295487/6583787/view",
    "https://www.saatchiart.com/art/Collage-Purple-1-Mulch-Series/1295487/6583781/view",
    "https://www.saatchiart.com/art/Collage-Close-Up-Mulch-Series/1295487/6583777/view",
    "https://www.saatchiart.com/art/Collage-Society-Mulch-Series/1295487/6583753/view",
    "https://www.saatchiart.com/art/Collage-Pieces-Of-Red/1295487/6583729/view",
    "https://www.saatchiart.com/art/Collage-Red-And-Black-Mulch-Series/1295487/6583709/view",
    "https://www.saatchiart.com/art/Collage-Paper-Peace/1295487/6583693/view",
    "https://www.saatchiart.com/art/Collage-Honeycomb-Mulch-Series/1295487/6583683/view",
    "https://www.saatchiart.com/art/Collage-Wild-Zebra-2-Mulch-Series/1295487/6583651/view",
    "https://www.saatchiart.com/art/Collage-Wild-Zebra-1-Mulch-Series/1295487/6583633/view",
    "https://www.saatchiart.com/art/Collage-Work-Party-Mulch-Series/1295487/6583609/view",
    "https://www.saatchiart.com/art/Collage-Business-Mulch/1295487/6583595/view",
    "https://www.saatchiart.com/art/Collage-Office-Work-Mulch/1295487/6583581/view",
    "https://www.saatchiart.com/art/Sculpture-Jaguar/1295487/6513325/view",
    "https://www.saatchiart.com/art/Sculpture-Megapixels/1295487/6513307/view",
    "https://www.saatchiart.com/art/Sculpture-Oyster-Mushrooms/1295487/6513293/view",
    "https://www.saatchiart.com/art/Sculpture-Esm-S17/1295487/6513257/view",
    "https://www.saatchiart.com/art/Painting-Fire-Flow/1295487/6513221/view",
    "https://www.saatchiart.com/art/Painting-Owls-In-Fall/1295487/6513209/view",
    "https://www.saatchiart.com/art/Painting-Connectivity/1295487/6513163/view",
    "https://www.saatchiart.com/art/Painting-Atomic-Flow/1295487/6513149/view",
    "https://www.saatchiart.com/art/Painting-Trees/1295487/6513127/view",
    "https://www.saatchiart.com/art/Painting-Animal-Kingdom/1295487/6513109/view",
    "https://www.saatchiart.com/art/Painting-Clean-Hands/1295487/6513085/view",
    "https://www.saatchiart.com/art/Painting-Reflection/1295487/6513075/view",
    "https://www.saatchiart.com/art/Painting-Eggs-And-Eyes/1295487/6492629/view",
    "https://www.saatchiart.com/art/Painting-Moon-Dance/1295487/6492627/view",
    "https://www.saatchiart.com/art/Painting-Floating-Leaves/1295487/6492617/view",
    "https://www.saatchiart.com/art/Painting-Arrowheads/1295487/6492613/view",
    "https://www.saatchiart.com/art/Painting-Campground/1295487/6492597/view",
    "https://www.saatchiart.com/art/Painting-Puzzle/1295487/6492595/view",
    "https://www.saatchiart.com/art/Painting-Streams-And-Ponds/1295487/6492583/view",
    "https://www.saatchiart.com/art/Painting-Cluster-Of-Caps/1295487/6492577/view",
    "https://www.saatchiart.com/art/Painting-Duck-Pond/1295487/6492573/view",
    "https://www.saatchiart.com/art/Painting-Creek-Bottom/1295487/6492497/view",
    "https://www.saatchiart.com/art/Painting-Organic-Mushrooms/1295487/6492491/view",
    "https://www.saatchiart.com/art/Painting-Stones/1295487/6492487/view",
    "https://www.saatchiart.com/art/Painting-Cubes/1295487/6492481/view",
    "https://www.saatchiart.com/art/Painting-Seed-Pods/1295487/6492463/view",
    "https://www.saatchiart.com/art/Painting-Excited-Bird/1295487/6492447/view",
    "https://www.saatchiart.com/art/Painting-Mushroom-Exclamation/1295487/6492441/view",
    "https://www.saatchiart.com/art/Painting-Snake-And-Rocks/1295487/6492431/view",
    "https://www.saatchiart.com/art/Painting-Shapeshifter/1295487/6492415/view",
    "https://www.saatchiart.com/art/Painting-Coiled-Snake/1295487/6492413/view",
    "https://www.saatchiart.com/art/Painting-Avacado-Snack/1295487/6492407/view",
    "https://www.saatchiart.com/art/Painting-Gold-Shapes/1295487/6492375/view",
    "https://www.saatchiart.com/art/Painting-Musical-Embrace/1295487/6492355/view",
    "https://www.saatchiart.com/art/Painting-Organic-Food/1295487/6492337/view",
    "https://www.saatchiart.com/art/Painting-Snake-Eggs/1295487/6492325/view",
    "https://www.saatchiart.com/art/Painting-Brush-Strokes/1295487/6492323/view",
    "https://www.saatchiart.com/art/Painting-Blanket/1295487/6492319/view",
    "https://www.saatchiart.com/art/Painting-Dance/1295487/6492311/view",
    "https://www.saatchiart.com/art/Painting-Bloom/1295487/6492303/view",
    "https://www.saatchiart.com/art/Painting-Organic-Shapes/1295487/6492289/view",
    "https://www.saatchiart.com/art/Painting-Silver/1295487/6483881/view",
    "https://www.saatchiart.com/art/Painting-Fortune/1295487/6483865/view",
    "https://www.saatchiart.com/art/Painting-Transformation/1295487/6483815/view",
    "https://www.saatchiart.com/art/Painting-Golden-Nugget/1295487/6483777/view",
    "https://www.saatchiart.com/art/Painting-Golden-Rule/1295487/6483759/view",
    "https://www.saatchiart.com/art/Painting-Portal/1295487/6483753/view",
    "https://www.saatchiart.com/art/Painting-Feather-Trees/1295487/6447005/view",
    "https://www.saatchiart.com/art/Painting-Magic-Carpet/1295487/6446995/view",
    "https://www.saatchiart.com/art/Painting-Screen/1295487/6446983/view",
    "https://www.saatchiart.com/art/Painting-Spring-Blooms/1295487/6446977/view",
    "https://www.saatchiart.com/art/Painting-Celebrate/1295487/6446967/view",
    "https://www.saatchiart.com/art/Painting-Anemones/1295487/6446959/view",
    "https://www.saatchiart.com/art/Painting-Coral/1295487/6446941/view",
    "https://www.saatchiart.com/art/Painting-Existance/1295487/6446929/view",
    "https://www.saatchiart.com/art/Painting-Fireworks/1295487/6446913/view",
    "https://www.saatchiart.com/art/Painting-Synapse/1295487/6446909/view",
    "https://www.saatchiart.com/art/Painting-Stick-Men/1295487/6446901/view",
    "https://www.saatchiart.com/art/Painting-Descending/1295487/6446893/view",
    "https://www.saatchiart.com/art/Painting-Lifeforce/1295487/6446799/view",
    "https://www.saatchiart.com/art/Painting-Turquoise-And-Peppers/1295487/6446775/view",
    "https://www.saatchiart.com/art/Painting-Turquoise-Blend/1295487/6446755/view",
    "https://www.saatchiart.com/art/Painting-Turquoise-Stretch/1295487/6446705/view",
    "https://www.saatchiart.com/art/Painting-Turquoise-Circuit-Board/1295487/6446693/view",
    "https://www.saatchiart.com/art/Painting-Blast-Of-Blue-On-Red/1295487/6446665/view",
    "https://www.saatchiart.com/art/Painting-Blue-Gold/1295487/6446651/view",
    "https://www.saatchiart.com/art/Painting-Blue-Glacier/1295487/6446603/view",
    "https://www.saatchiart.com/art/Painting-Blue-Wave/1295487/6446583/view",
    "https://www.saatchiart.com/art/Painting-Blue-Mesh/1295487/6446557/view",
    "https://www.saatchiart.com/art/Painting-Cold-Blue/1295487/6446543/view",
    "https://www.saatchiart.com/art/Painting-Blue-Storm/1295487/6446503/view",
    "https://www.saatchiart.com/art/Printmaking-No-Public-Shrooms-Limited-Edition-Of-1/1295487/6444945/view",
    "https://www.saatchiart.com/art/Printmaking-No-Public-Shrooms-Limited-Edition-Of-1/1295487/6444917/view",
    "https://www.saatchiart.com/art/Printmaking-Start-Sign-Limited-Edition-Of-1/1295487/6444891/view",
    "https://www.saatchiart.com/art/Printmaking-Right-Way-Limited-Edition-Of-1/1295487/6444853/view",
    "https://www.saatchiart.com/art/Installation-No-Porking/1295487/6444805/view",
    "https://www.saatchiart.com/art/Painting-Gold-Series-006/1295487/6412863/view",
    "https://www.saatchiart.com/art/Painting-Gold-Series-005/1295487/6412831/view",
    "https://www.saatchiart.com/art/Painting-Gold-Series-004/1295487/6412815/view",
    "https://www.saatchiart.com/art/Painting-Gold-Series-003/1295487/6412813/view",
    "https://www.saatchiart.com/art/Painting-Gold-Series-002/1295487/6412799/view",
    "https://www.saatchiart.com/art/Painting-Gold-Series-001/1295487/6412791/view",
    "https://www.saatchiart.com/art/Painting-Waves/1295487/6364287/view"
]

def apply_urls():
    path = r"c:\sandbox\esm\artwork_data.json"
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    updates = 0
    
    # Create lookup map from user URLs (slug -> url)
    # The slug in the URL is the part after /art/
    # e.g. "Painting-Caviar" from ".../art/Painting-Caviar/..."
    # Warning: The JSON might store slug as "painting_caviar" or "painting_caviar_..."
    
    slug_map = {}
    
    for url in user_urls:
        # Extract slug from URL
        # Format: /art/{SLUG}/{ARTIST_ID}/{ARTWORK_ID}/view
        match = re.search(r'/art/([^/]+)/', url)
        if match:
            url_slug = match.group(1).lower()
            # Normalize slug (replace dashes with spaces for fuzzy matching maybe?)
            # Or just normalize checking against normalized JSON title/slug
            slug_map[url_slug] = url
        else:
            print(f"Skipping malformed URL: {url}")

    # Iterate JSON and match
    for item in data:
        # Strategy:
        # 1. Match item['slug'].replace('_', '-') against url_slug (exact)
        # 2. Match item['title'] loosely against url_slug
        
        item_slug = item.get('slug', '').replace('_', '-').lower()
        title = item.get('title', '').lower().replace(' ', '-')
        
        matched_url = None
        
        # Exact match attempt
        if item_slug in slug_map:
            matched_url = slug_map[item_slug]
        
        if not matched_url:
             # Try partial matching or fuzzy logic
             # e.g. URL slug "painting-caviar", item slug "painting-caviar"
             # e.g. URL slug "collage-pieces-of-red", item slug "pieces-of-red" (might miss medium prefix)
             
             for u_slug, u_url in slug_map.items():
                 # Check if item_slug is contained in url_slug or vice versa
                 if item_slug in u_slug or u_slug in item_slug:
                     # Heuristic: Check similarity or common words
                     # Verify artwork ID in URL if possible? No we don't have it in JSON reliably
                     
                     # Check if specific important words form the title match
                     matched_url = u_url
                     break
                     
        if not matched_url:
             # Try stripping "painting-", "collage-", "sculpture-" prefixes from url slug
             clean_title = title.replace('painting-', '').replace('collage-', '').replace('sculpture-', '')
             
             for u_slug, u_url in slug_map.items():
                 u_clean = u_slug.replace('painting-', '').replace('collage-', '').replace('sculpture-', '')
                 if clean_title == u_clean:
                     matched_url = u_url
                     break

        if matched_url:
            if item.get('saatchi_url') != matched_url:
                print(f"Updating '{item['title']}':\n  OLD: {item.get('saatchi_url')}\n  NEW: {matched_url}")
                item['saatchi_url'] = matched_url
                updates += 1
            else:
                pass # Already matches
        else:
            # print(f"No match found for JSON item: {item['title']} ({item['slug']})")
            pass

    if updates > 0:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        print(f"Successfully updated {updates} artwork URLs in JSON.")
    else:
        print("No updates needed.")

if __name__ == "__main__":
    apply_urls()
