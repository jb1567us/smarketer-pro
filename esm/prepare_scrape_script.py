import json

# Read deduplicated data
data = []
try:
    with open('artwork_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
except Exception as e:
    print(f"Error reading artwork_data.json: {e}")
    exit(1)

# Prepare list for JS
js_list = []
for item in data:
    if item.get('saatchi_url'):
        js_list.append({
            'id': item['id'],
            'title': item['title'],
            'saatchi_url': item['saatchi_url']
        })

print(f"Prepared {len(js_list)} items for scraping.")

# JS Template
js_content = f"""
// MASS SCRAPE SAATCHI
(async () => {{
    const artworkList = {json.dumps(js_list)};

    console.log(`Starting scan of ${{artworkList.length}} items...`);
    const results = [];
    const errors = [];

    const wait = ms => new Promise(r => setTimeout(r, ms));

    for (let i = 0; i < artworkList.length; i++) {{
        const item = artworkList[i];
        // console.log(`[${{i + 1}}/${{artworkList.length}}] Fetching: ${{item.title}}`);

        try {{
            const resp = await fetch(item.saatchi_url);
            if (!resp.ok) throw new Error(`Status ${{resp.status}}`);
            const html = await resp.text();
            const doc = new DOMParser().parseFromString(html, 'text/html');
            const extracted = {{ ...item }};

            // 1. Description
            const descEl = Array.from(doc.querySelectorAll('h3')).find(h => h.innerText.toUpperCase().includes('ABOUT THE ARTWORK'));
            if (descEl && descEl.nextElementSibling) {{
                extracted.description = descEl.nextElementSibling.innerText.trim();
            }} else {{
                const metaDesc = doc.querySelector('[itemprop="description"]');
                if (metaDesc) extracted.description = metaDesc.innerText.trim();
            }}

            // 2. Metadata Lines
            const extractLabel = (label) => {{
                // Strategy: Find text node, go to next sibling or parent's next sibling
                const els = Array.from(doc.querySelectorAll('*'));
                const labelEl = els.find(e => e.innerText && e.innerText.trim().startsWith(label) && e.children.length < 2 && e.tagName !== 'SCRIPT');
                if (labelEl) {{
                    const text = labelEl.innerText.trim();
                    if (text.length > label.length + 2) {{
                        return text.replace(label, '').replace(/^:/, '').trim();
                    }}
                    if (labelEl.nextElementSibling) return labelEl.nextElementSibling.innerText.trim();
                    if (labelEl.parentElement && labelEl.parentElement.nextElementSibling) return labelEl.parentElement.nextElementSibling.innerText.trim();
                }}
                return null;
            }};

            extracted.year = extractLabel("Year Created");
            extracted.styles = extractLabel("Styles");
            extracted.mediumsDetailed = extractLabel("Mediums");
            extracted.frame = extractLabel("Frame");
            extracted.readyToHang = extractLabel("Ready to Hang");
            extracted.packaging = extractLabel("Packaging");
            extracted.shippingFrom = extractLabel("Ships From");

            if (extracted.description && extracted.description.includes("Year Created:")) {{
                extracted.description = extracted.description.split("Year Created:")[0].trim();
            }}

            results.push(extracted);

        }} catch (e) {{
            console.error(`Failed ${{item.title}}:`, e);
            errors.push(item);
        }}

        // Polite delay
        await wait(200);
    }}

    console.log("SCRAPING COMPLETE");
    console.log(JSON.stringify(results)); // Output finding
}})();
"""

with open('mass_scrape_saatchi.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print("Generated mass_scrape_saatchi.js")
