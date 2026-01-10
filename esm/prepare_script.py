import json
import re
import base64

# Read Data directly
with open('artwork_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Read JS Template/Logic
with open('mass_create_pages.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Split data into chunks of 10
chunks = [data[i:i + 10] for i in range(0, len(data), 10)]

# Extract Template
# tmpl_match = re.search(r'const layoutTemplate = `(.*?)`;', content, re.DOTALL)
# if not tmpl_match:
#     print("Template not found")
#     exit(1)
# template = tmpl_match.group(1)

# Read Template from HTML file directly (contains wp:html fix)
with open('PREMIUM_ARTWORK_LAYOUT_VERTICAL.html', 'r', encoding='utf-8') as f:
    template = f.read()
# Minify template (remove newlines and extra spaces)
min_template = re.sub(r'\s+', ' ', template).replace('> <', '><')

# Extract Logic including constants
# Find start of constants
start_marker = 'const DEFAULT_PRICE'
start_idx = content.find(start_marker)
if start_idx == -1:
    print("Logic start not found")
    exit(1)

# Find end of validation/logic (before the call)
call_marker = 'processMassBatch();'
end_idx = content.rfind(call_marker)
if end_idx == -1:
    print("Logic end not found")
    exit(1)

logic = content[start_idx:end_idx].strip()

# logic needs to use window.MASS_DATA and window.layoutTemplate
logic = logic.replace('const artworkData =', '// const artworkData =')
logic = logic.replace('const layoutTemplate =', '// const layoutTemplate =')
# Fix Loop
logic = logic.replace('for (const item of artworkData)', 'for (const item of window.MASS_DATA)')
# Fix Logging
logic = logic.replace('${artworkData.length}', '${window.MASS_DATA.length}')
# Fix Template
logic = logic.replace('let content = layoutTemplate', """
                // SMART IMAGE CHECK
                // Try the default URL first (A-Day-at-the-LakePainting.jpg)
                let finalImageUrl = item.image_url;
                
                try {
                    const check1 = await fetch(finalImageUrl, { method: 'HEAD' });
                    if (!check1.ok) {
                         // If 404, try adding hyphen before Painting (A-Day-at-the-Lake-Painting.jpg)
                         const altUrl = finalImageUrl.replace(/Painting\.jpg$/, '-Painting.jpg');
                         console.log(`Image 404: ${finalImageUrl}. Trying: ${altUrl}`);
                         
                         const check2 = await fetch(altUrl, { method: 'HEAD' });
                         if (check2.ok) {
                             finalImageUrl = altUrl;
                             console.log(`FOUND alternative image: ${finalImageUrl}`);
                         } else {
                             // Try underscores as last resort
                             const underscoreUrl = finalImageUrl.replace(/-/g, '_').replace(/_Painting\.jpg$/, 'Painting.jpg');
                             const check3 = await fetch(underscoreUrl, { method: 'HEAD' });
                             if (check3.ok) {
                                 finalImageUrl = underscoreUrl;
                             } else {
                                 console.warn(`❌ Image not found for ${finalTitle}`);
                             }
                         }
                    }
                } catch (e) {
                    console.warn(`Could not verify image for ${finalTitle}, keeping default.`);
                }

                let content = window.layoutTemplate
                    .replace(/{{TITLE}}/g, finalTitle)
                    .replace(/{{IMAGE_URL}}/g, finalImageUrl) 
                    .replace(/{{PRICE}}/g, price)
                    .replace(/{{MEDIUM}}/g, medium)
                    .replace(/{{YEAR}}/g, item.year || '2024')
                    .replace(/{{STYLES}}/g, item.styles || 'Abstract')
                    .replace(/{{MEDIUMS_DETAILED}}/g, item.mediumsDetailed || medium)
                    .replace(/{{FRAME}}/g, item.frame || 'Not Framed')
                    .replace(/{{PACKAGING}}/g, item.packaging || 'Ships Rolled in a Tube')
                    .replace(/{{SHIPPING}}/g, item.shippingFrom || 'United States')""")



# Remove JS comments
logic = re.sub(r'//.*', '', logic)

# Encode template
b64_tmpl = base64.b64encode(min_template.encode('utf-8')).decode('utf-8')


# Split data into Super Chunks of 10 (Smaller batches for stability)
super_chunks = [data[i:i + 10] for i in range(0, len(data), 10)]


# Generate Single Unified Manual Script
all_items = []
for sc in super_chunks:
    all_items.extend(sc)

# Final complete JS for manual use
manual_js_content = f"""
// MASS MIGRATION SCRIPT - MANUAL EXECUTION
// 1. SETUP (Template & Logic)
window.layoutTemplate = new TextDecoder().decode(Uint8Array.from(atob("{b64_tmpl}"), c => c.charCodeAt(0)));

{logic}

// 2. DATA (ALL ITEMS)
window.MASS_DATA = {json.dumps(all_items)};

// 3. EXECUTE
(async () => {{
    console.log("Starting MASS MIGRATION for " + window.MASS_DATA.length + " items...");
    console.log("This process may take 10-20 minutes. Please keep this tab open.");
    
    if (typeof processMassBatch !== 'function') {{
        console.error("processMassBatch is not defined!");
        return;
    }}
    
    await processMassBatch();
    
    console.log("-----------------------------------------");
    console.log("MIGRATION COMPLETE.");
    console.log("-----------------------------------------");
    alert("Migration Complete!");
}})();
"""

manual_filename = 'mass_migration_full.js'
with open(manual_filename, 'w', encoding='utf-8') as f:
    f.write(manual_js_content.strip())

print(f"Generated {manual_filename} with {len(all_items)} items.")
