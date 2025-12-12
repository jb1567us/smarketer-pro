import json

# Load artwork data
with open(r'C:\sandbox\esm\artwork_data.json', 'r', encoding='utf-8') as f:
    artworks = json.load(f)

# Filter for missing items
missing_items = []
for artwork in artworks:
    image_url = artwork.get('image_url')
    if (not image_url or image_url.strip() == "") and artwork.get('saatchi_url'):
        missing_items.append({
            'id': artwork.get('id'),
            'title': artwork.get('title'),
            'saatchi_url': artwork.get('saatchi_url')
        })

print(f"Generating scraper for {len(missing_items)} items...")

# Create the JS script content
js_content = f'''
// SCRAPE MISSING IMAGES
(async () => {{
    const artworkList = {json.dumps(missing_items)};

    console.log(`Starting image scrape for ${{artworkList.length}} items...`);
    const results = [];
    const errors = [];

    const wait = ms => new Promise(r => setTimeout(r, ms));

    for (let i = 0; i < artworkList.length; i++) {{
        const item = artworkList[i];
        console.log(`[${{i + 1}}/${{artworkList.length}}] Fetching: ${{item.title}}`);

        try {{
            const resp = await fetch(item.saatchi_url);
            if (!resp.ok) throw new Error(`Status ${{resp.status}}`);
            const html = await resp.text();
            const doc = new DOMParser().parseFromString(html, 'text/html');
            
            const extracted = {{ ...item }};
            
            // Extract Image URL
            // Strategy 1: og:image meta tag (Most reliable)
            const ogImage = doc.querySelector('meta[property="og:image"]');
            if (ogImage) {{
                extracted.image_url = ogImage.content;
            }} else {{
                // Strategy 2: Main image element
                const mainImg = doc.querySelector('[data-role="main-image"], .artwork-image img');
                if (mainImg) extracted.image_url = mainImg.src;
            }}

            if (extracted.image_url) {{
                console.log(`  found image: ${{extracted.image_url.substring(0, 30)}}...`);
                results.push(extracted);
            }} else {{
                console.warn(`  NO IMAGE FOUND for ${{item.title}}`);
                errors.push(item);
            }}

        }} catch (e) {{
            console.error(`Failed ${{item.title}}:`, e);
            errors.push(item);
        }}

        // Polite delay
        await wait(500);
    }}

    console.log("SCRAPING COMPLETE");
    console.log("=== COPY THE JSON BELOW ===");
    console.log(JSON.stringify(results));
    console.log("===========================");
    
    // Auto-download
    const blob = new Blob([JSON.stringify(results, null, 2)], {{ type: 'application/json' }});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'scraped_images.json';
    a.click();
}})();
'''

with open(r'C:\sandbox\esm\scrape_missing_images.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print("Created C:\\sandbox\\esm\\scrape_missing_images.js")
