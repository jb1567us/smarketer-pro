// SAATCHI METADATA SCRAPER
// Run this script in the Browser Console on correct artwork page or while on saatchiart.com
// It will fetch all the artwork pages and extract rich metadata.

(async () => {
    // 1. DATA TO SCRAPE
    // (Pasted from artwork_data.json)
    const artworkList = [
        { "id": 1109, "title": "A Day at the Lake Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-A-day-at-the-lake/1295487/6105151/view" },
        { "id": 1108, "title": "A day at the park Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-A-day-at-the-park/1295487/6105309/view" },
        { "id": 1107, "title": "A day at the beach Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-A-day-at-the-beach/1295487/6105263/view" },
        { "id": 1106, "title": "Gold Series 011 Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Gold-Series-011/1295487/6131379/view" },
        { "id": 1105, "title": "Gold Series 010 Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Gold-Series-010/1295487/6131393/view" },
        { "id": 1104, "title": "Gold Series 009 Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Gold-Series-009/1295487/6131427/view" },
        { "id": 1103, "title": "Gold Series 008 Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Gold-Series-008/1295487/6131441/view" },
        { "id": 1102, "title": "Gold Series 007 Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Gold-Series-007/1295487/6131477/view" },
        { "id": 1101, "title": "Red Planet Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Red-Planet/1295487/6131365/view" },
        { "id": 1100, "title": "Portal Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Portal/1295487/6483753/view" },
        { "id": 108, "title": "Portal 2 Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Portal-2/1295487/8146546/view" },
        { "id": 125, "title": "Abstract Landscape Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Abstract-Landscape/1295487/8123730/view" },
        { "id": 110, "title": "self portrait 1 Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Self-Portrait-1/1295487/8125469/view" },
        { "id": 102, "title": "Convergence Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Convergence/1295487/8754060/view" },
        { "id": 106, "title": "Puzzled Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Puzzled/1295487/8146584/view" },
        { "id": 104, "title": "Finger print Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Finger-Print/1295487/8754025/view" },
        { "id": 105, "title": "Sheet Music Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Sheet-Music/1295487/8146759/view" },
        { "id": 103, "title": "Meeting in the Middle Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Meeting-In-The-Middle/1295487/8754042/view" },
        { "id": 101, "title": "Caviar Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Caviar/1295487/12292979/view" }
    ];

    console.log(`Starting scan of ${artworkList.length} items...`);
    const results = [];
    const errors = [];

    // DELAY HELPER
    const wait = ms => new Promise(r => setTimeout(r, ms));

    // MAIN LOOP
    for (let i = 0; i < artworkList.length; i++) {
        const item = artworkList[i];
        console.log(`[${i + 1}/${artworkList.length}] Fetching: ${item.title}`);

        try {
            const resp = await fetch(item.saatchi_url);
            if (!resp.ok) throw new Error(`Status ${resp.status}`);
            const html = await resp.text();

            // PARSE HTML
            const doc = new DOMParser().parseFromString(html, 'text/html');

            // EXTRACT DATA logic
            const extracted = { ...item };

            // 1. Description (About the Artwork)
            // Look for "ABOUT THE ARTWORK" header, then getting following text
            // The structure is often: <h3>About The Artwork</h3> <div>...content...</div>
            // Or just a specific class.
            const allText = doc.body.innerText;
            // Better key-value extraction?

            // Description is usually in a div with specific class or after "About The Artwork"
            // Let's try selectors first
            const descEl = Array.from(doc.querySelectorAll('h3')).find(h => h.innerText.toUpperCase().includes('ABOUT THE ARTWORK'));
            if (descEl && descEl.nextElementSibling) {
                extracted.description = descEl.nextElementSibling.innerText.trim();
            } else {
                // Try looking for <div itemprop="description">
                const metaDesc = doc.querySelector('[itemprop="description"]');
                if (metaDesc) extracted.description = metaDesc.innerText.trim();
            }

            // 2. Metadata Lines (Year, Styles, Mediums) - These are usually in a DL or UL list
            // Or divs with labels.
            // Example: <div ...>Year Created:</div> <div>2024</div>

            const extractLabel = (label) => {
                // Find element with text including label
                // Often looks like: <dt>Year Created:</dt> <dd>2024</dd>
                // Or <div>Year Created: <span>2024</span></div>

                // Strategy: Find text node, go to next sibling or parent's next sibling
                const els = Array.from(doc.querySelectorAll('*'));
                const labelEl = els.find(e => e.innerText && e.innerText.trim().startsWith(label) && e.children.length < 2 && e.tagName !== 'SCRIPT');

                if (labelEl) {
                    // Check if the value is INSIDE (e.g. "Year Created: 2024")
                    const text = labelEl.innerText.trim();
                    if (text.length > label.length + 2) {
                        return text.replace(label, '').replace(/^:/, '').trim();
                    }
                    // Check Next Sibling
                    if (labelEl.nextElementSibling) return labelEl.nextElementSibling.innerText.trim();
                    // Check Parent's Next Sibling (if label is wrapped)
                    if (labelEl.parentElement && labelEl.parentElement.nextElementSibling) return labelEl.parentElement.nextElementSibling.innerText.trim();
                }
                return null;
            };

            extracted.year = extractLabel("Year Created") || extracted.year;
            extracted.styles = extractLabel("Styles");
            extracted.mediumsDetailed = extractLabel("Mediums"); // "Ink, Paper"
            extracted.frame = extractLabel("Frame");
            extracted.readyToHang = extractLabel("Ready to Hang");
            extracted.packaging = extractLabel("Packaging");
            extracted.shippingFrom = extractLabel("Ships From");

            // Clean up Description if it contains metadata
            if (extracted.description && extracted.description.includes("Year Created:")) {
                extracted.description = extracted.description.split("Year Created:")[0].trim();
            }

            results.push(extracted);
            console.log("   -> Success!");

        } catch (e) {
            console.error("   -> Failed!", e);
            errors.push(item);
            results.push(item); // Keep original
        }

        // Random wait to be polite
        await wait(200 + Math.random() * 500);
    }

    console.log("-----------------------------------");
    console.log("SCRAPING COMPLETE.");
    console.log(`Success: ${results.length - errors.length}, Failures: ${errors.length}`);

    // DOWNLOAD JSON
    const blob = new Blob([JSON.stringify(results, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'enhanced_artwork_data.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    console.log("Downloading... enhanced_artwork_data.json");

})();
