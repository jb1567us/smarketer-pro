import json

# Load the data
with open(r'C:\sandbox\esm\artwork_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Allow us to generate a smaller chunk for testing or the full batch
# We will generate a JS file that contains the data and the logic.

items_payload = []

for item in data:
    if not item.get('wordpress_id'):
        continue
    
    # Construct Tags
    tags = set()
    
    # 1. Colors
    if 'detected_colors' in item:
        for c in item['detected_colors']:
            tags.add(c)
            
    # 2. Styles
    if item.get('styles'):
        for s in item['styles'].split(','):
             tags.add(s.strip())
             
    # 3. Mediums
    if item.get('mediumsDetailed'):
        for m in item['mediumsDetailed'].split(','):
            tags.add(m.strip())
            
    # 4. Dimensions logic
    try:
        w = float(item.get('width', 0))
        h = float(item.get('height', 0))
        if w >= 48 or h >= 48: 
            tags.add('Large')
            tags.add('Statement Piece')
        if w > 0 and h > 0 and abs(w - h) < 1:
            tags.add('Square')
    except:
        pass
        
    # Clean tags
    clean_tags = [t for t in tags if t and len(t) > 1]
    
    items_payload.append({
        'id': item['wordpress_id'],
        'title': item['title'],
        'tags': list(clean_tags)
    })

# Convert to JSON string for JS embedding
payload_json = json.dumps(items_payload)

js_content = f"""
// Apply Tags to Pages Script
// Run this in the WordPress Console

(async function() {{
    const items = {payload_json};
    
    console.log(`Starting tag update for ${{items.length}} pages...`);
    
    // Cache for tag IDs to avoid repeated API lookup calls
    const tagCache = {{}};
    
    async function getOrCreateTagId(tagName) {{
        if (tagCache[tagName]) return tagCache[tagName];
        
        try {{
            // 1. Search for existing tag
            const search = await wp.apiFetch({{ path: `/wp/v2/tags?search=${{encodeURIComponent(tagName)}}` }});
            // Exact match check
            const found = search.find(t => t.name.toLowerCase() === tagName.toLowerCase());
            
            if (found) {{
                tagCache[tagName] = found.id;
                return found.id;
            }}
            
            // 2. Create if not found
            const newTag = await wp.apiFetch({{
                path: '/wp/v2/tags',
                method: 'POST',
                data: {{ name: tagName }}
            }});
            
            tagCache[tagName] = newTag.id;
            return newTag.id;
            
        }} catch (e) {{
            console.warn(`Could not handle tag '${{tagName}}':`, e.message);
            return null;
        }}
    }}

    let successCount = 0;
    
    for (const item of items) {{
        if (!item.tags || item.tags.length === 0) continue;
        
        console.log(`Processing ${{item.title}} (${{item.id}})...`);
        
        // Resolve all tag IDs
        const tagIds = [];
        for (const tagName of item.tags) {{
            const id = await getOrCreateTagId(tagName);
            if (id) tagIds.push(id);
        }}
        
        if (tagIds.length === 0) continue;
        
        // Update Page
        try {{
            await wp.apiFetch({{
                path: `/wp/v2/pages/${{item.id}}`,
                method: 'POST',
                data: {{ tags: tagIds }}
            }});
            successCount++;
            console.log(`✅ Updated ${{item.title}} with ${{tagIds.length}} tags.`);
        }} catch (e) {{
            console.error(`❌ Failed to update ${{item.title}}:`, e.message);
        }}
        
        // Small delay to be nice to server
        await new Promise(r => setTimeout(r, 100)); // 100ms
    }}
    
    console.log(`Finished! Updated ${{successCount}} pages.`);
    alert(`Tag Update Complete! Updated ${{successCount}} pages.`);
}})();
"""

with open(r'C:\sandbox\esm\apply_tags_to_pages.js', 'w', encoding='utf-8') as f:
    f.write(js_content)
    
print("Generated C:\\sandbox\\esm\\apply_tags_to_pages.js")
