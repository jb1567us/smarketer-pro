import json

DATA_FILE = r'C:\sandbox\esm\artwork_data.json'
with open(DATA_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)

updated_count = 0

print("Cleaning tags...")

for item in data:
    # 1. Clean existing styles
    raw_styles = item.get('styles', '')
    if raw_styles:
        # Split, strip, filter
        style_list = [s.strip() for s in raw_styles.split(',')]
        
        # REMOVE 'Art Deco' globally (User feedback: "Art's echo wasn't really there")
        if 'Art Deco' in style_list:
            style_list.remove('Art Deco')
            
        # Join back
        item['styles'] = ", ".join(style_list)
        
    # 2. Add Heuristic Tags (Patterns/Styles)
    # derived_tags list to be merged during PHP generation, 
    # but let's store them in a new field 'smart_tags' or just clean up 'keywords'?
    # Actually, the PHP generator reads 'styles' and 'detected_colors'.
    # I should update 'styles' to include the new smart tags or create a 'smart_tags' field 
    # and update the generator to read it.
    
    # I'll update 'styles' string to keep it simple for the existing pipeline.
    
    additional_tags = set()
    title_lower = item['title'].lower()
    
    # Geometric / Pattern detection
    geo_keywords = ['geometric', 'structure', 'cube', 'square', 'line', 'grid', 'puzzle', 'block', 'granular', 'maze', 'tech', 'circuit']
    if any(k in title_lower for k in geo_keywords):
        additional_tags.add('Geometric')
        additional_tags.add('Structured')

    # Organic / Flow detection
    organic_keywords = ['flow', 'river', 'wave', 'water', 'organic', 'bloom', 'nature', 'tree', 'flower', 'leaf', 'cloud', 'smoke']
    if any(k in title_lower for k in organic_keywords):
        additional_tags.add('Organic')
        additional_tags.add('Fluid')

    # Minimalist vs Vibrant (based on Color Count from detected_colors)
    colors = item.get('detected_colors', [])
    if colors:
        if len(colors) <= 2:
            additional_tags.add('Minimalist')
        elif len(colors) >= 5: # If visual analysis returned lots of distinct colors (assuming it was capable)
            # My simple analyzer usually returns top 5. If all 5 are distinct?
            # Let's rely on 'Colorful' if title says so or if we have [Red, Blue, Green...]
            pass
            
        # High Contrast Check
        if 'Black' in colors and 'White' in colors:
            additional_tags.add('High Contrast')
        if 'Black' in colors and 'Gold' in colors:
            additional_tags.add('Luxury')

    # Merge into styles
    current_styles = [s.strip() for s in item.get('styles', '').split(',') if s.strip()]
    
    # Combine
    final_styles = set(current_styles) | additional_tags
    
    # Remove duplicates and empty
    final_list = [s for s in final_styles if s]
    
    new_styles_str = ", ".join(final_list)
    
    if new_styles_str != raw_styles:
        item['styles'] = new_styles_str
        updated_count += 1

print(f"Updated {updated_count} items with cleaner styles and smart patterns.")

with open(DATA_FILE, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4)
