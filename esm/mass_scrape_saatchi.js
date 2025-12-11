
// MASS SCRAPE SAATCHI
(async () => {
    const artworkList = [{"id": 1696, "title": "A Day at the Lake", "saatchi_url": "https://www.saatchiart.com/art/Painting-A-day-at-the-lake/1295487/6105151/view"}, {"id": 1697, "title": "A day at the park", "saatchi_url": "https://www.saatchiart.com/art/Painting-A-day-at-the-park/1295487/6105309/view"}, {"id": 1698, "title": "A day at the beach", "saatchi_url": "https://www.saatchiart.com/art/Painting-A-day-at-the-beach/1295487/6105263/view"}, {"id": 1699, "title": "Gold Series 011", "saatchi_url": "https://www.saatchiart.com/art/Painting-Gold-Series-011/1295487/6131379/view"}, {"id": 1700, "title": "Gold Series 010", "saatchi_url": "https://www.saatchiart.com/art/Painting-Gold-Series-010/1295487/6131393/view"}, {"id": 1701, "title": "Gold Series 009", "saatchi_url": "https://www.saatchiart.com/art/Painting-Gold-Series-009/1295487/6131427/view"}, {"id": 1702, "title": "Gold Series 008", "saatchi_url": "https://www.saatchiart.com/art/Painting-Gold-Series-008/1295487/6131441/view"}, {"id": 1703, "title": "Gold Series 007", "saatchi_url": "https://www.saatchiart.com/art/Painting-Gold-Series-007/1295487/6131477/view"}, {"id": 1704, "title": "Red Planet", "saatchi_url": "https://www.saatchiart.com/art/Painting-Red-Planet/1295487/6131365/view"}, {"id": 1674, "title": "Portal", "saatchi_url": "https://www.saatchiart.com/art/Painting-Portal/1295487/6483753/view"}, {"id": 1706, "title": "Portal 2", "saatchi_url": "https://www.saatchiart.com/art/Painting-Portal-2/1295487/8146546/view"}, {"id": 1707, "title": "Abstract Landscape", "saatchi_url": "https://www.saatchiart.com/art/Painting-Abstract-Landscape/1295487/8123730/view"}, {"id": 1708, "title": "self portrait 1", "saatchi_url": "https://www.saatchiart.com/art/Painting-Self-Portrait-1/1295487/8125469/view"}, {"id": 1629, "title": "Convergence", "saatchi_url": "https://www.saatchiart.com/art/Painting-Convergence/1295487/8754060/view"}, {"id": 1630, "title": "Puzzled", "saatchi_url": "https://www.saatchiart.com/art/Painting-Puzzled/1295487/8146584/view"}, {"id": 1709, "title": "Finger print", "saatchi_url": "https://www.saatchiart.com/art/Painting-Finger-Print/1295487/8754025/view"}, {"id": 1710, "title": "Sheet Music", "saatchi_url": "https://www.saatchiart.com/art/Painting-Sheet-Music/1295487/8146759/view"}, {"id": 1711, "title": "Meeting in the Middle", "saatchi_url": "https://www.saatchiart.com/art/Painting-Meeting-In-The-Middle/1295487/8754042/view"}, {"id": 1585, "title": "Caviar", "saatchi_url": "https://www.saatchiart.com/art/Painting-Caviar/1295487/12292979/view"}, {"id": 107, "title": "Heart Work Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Heart-Work/1295487/8146572/view"}, {"id": 109, "title": "Portal 1 Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Portal-1/1295487/8146533/view"}, {"id": 111, "title": "Morning Joe Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Morning-Joe/1295487/8125458/view"}, {"id": 112, "title": "Unity Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Unity/1295487/8125409/view"}, {"id": 113, "title": "Dog on a bike Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Dog-On-A-Bike/1295487/8125271/view"}, {"id": 114, "title": "Water People Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Water-People/1295487/7363373/view"}, {"id": 115, "title": "Towers Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Towers/1295487/7363345/view"}, {"id": 116, "title": "Granular Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Granular/1295487/7363339/view"}, {"id": 117, "title": "Puzzle 2 Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Puzzle-2/1295487/7363331/view"}, {"id": 118, "title": "Puzzle 1 Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Puzzle-1/1295487/7363317/view"}, {"id": 119, "title": "Trichome Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Trichome/1295487/7363313/view"}, {"id": 120, "title": "Trichomes Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Trichomes/1295487/7363299/view"}, {"id": 121, "title": "Grill Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Grill/1295487/6783253/view"}, {"id": 122, "title": "Quilted Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Quilted/1295487/6783247/view"}, {"id": 123, "title": "Interactions Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Interactions/1295487/6783239/view"}, {"id": 124, "title": "Rush Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Rush/1295487/6783231/view"}, {"id": 125, "title": "Yorkie Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Yorkie/1295487/6783225/view"}, {"id": 126, "title": "Night Sky Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Night-Sky/1295487/6783211/view"}, {"id": 127, "title": "Bold Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Bold/1295487/6783203/view"}, {"id": 128, "title": "Climbing Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Climbing/1295487/6783197/view"}, {"id": 129, "title": "Dance Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Dance/1295487/6783193/view"}, {"id": 130, "title": "Smoke Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Smoke/1295487/6783181/view"}, {"id": 131, "title": "Motion Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Motion/1295487/6783137/view"}, {"id": 132, "title": "Listening Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Listening/1295487/6783125/view"}, {"id": 133, "title": "Synapses Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Synapses/1295487/6783101/view"}, {"id": 134, "title": "Microscope 7 Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Microscope-7/1295487/6782897/view"}, {"id": 135, "title": "Microscope 6 Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Microscope-6/1295487/6782859/view"}, {"id": 136, "title": "Microscope 5 Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Microscope-5/1295487/6782839/view"}, {"id": 137, "title": "Microscope 4 Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Microscope-4/1295487/6782817/view"}, {"id": 138, "title": "Microscope 3 Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Microscope-3/1295487/6782785/view"}, {"id": 139, "title": "Microscope 2 Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Microscope-2/1295487/6782755/view"}, {"id": 140, "title": "Microscope 1 Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Microscope-1/1295487/6782739/view"}, {"id": 141, "title": "Floating 6 - Rabbit Sculpture", "saatchi_url": "https://www.saatchiart.com/art/Sculpture-Floating-6-Rabbit/1295487/6627463/view"}, {"id": 142, "title": "Floating 5 - Moth Sculpture", "saatchi_url": "https://www.saatchiart.com/art/Sculpture-Floating-5-Moth/1295487/6627457/view"}, {"id": 143, "title": "Floating 4 - Vines Sculpture", "saatchi_url": "https://www.saatchiart.com/art/Sculpture-Floating-4-Vines/1295487/6627447/view"}, {"id": 144, "title": "Floating 3 - Tree Sculpture", "saatchi_url": "https://www.saatchiart.com/art/Sculpture-Floating-3-Tree/1295487/6627443/view"}, {"id": 145, "title": "Floating 2 - Butterfly Sculpture", "saatchi_url": "https://www.saatchiart.com/art/Sculpture-Floating-2-Butterfly/1295487/6627437/view"}, {"id": 146, "title": "Floating 1 - Cicada Sculpture", "saatchi_url": "https://www.saatchiart.com/art/Sculpture-Floating-1-Cicada/1295487/6627409/view"}, {"id": 147, "title": "Purple Night - Mulch Series Collage", "saatchi_url": "https://www.saatchiart.com/art/Collage-Purple-Night-Mulch-Series/1295487/6583797/view"}, {"id": 148, "title": "City at Night - Mulch Series Collage", "saatchi_url": "https://www.saatchiart.com/art/Collage-City-At-Night-Mulch-Series/1295487/6583787/view"}, {"id": 149, "title": "Purple 1 - Mulch Series Collage", "saatchi_url": "https://www.saatchiart.com/art/Collage-Purple-1-Mulch-Series/1295487/6583781/view"}, {"id": 150, "title": "Close up - Mulch Series Collage", "saatchi_url": "https://www.saatchiart.com/art/Collage-Close-Up-Mulch-Series/1295487/6583777/view"}, {"id": 151, "title": "Society - Mulch Series Collage", "saatchi_url": "https://www.saatchiart.com/art/Collage-Society-Mulch-Series/1295487/6583753/view"}, {"id": 152, "title": "Pieces of Red Collage", "saatchi_url": "https://www.saatchiart.com/art/Collage-Pieces-Of-Red/1295487/6583729/view"}, {"id": 153, "title": "Red and Black - Mulch Series Collage", "saatchi_url": "https://www.saatchiart.com/art/Collage-Red-And-Black-Mulch-Series/1295487/6583709/view"}, {"id": 154, "title": "Paper Peace Collage", "saatchi_url": "https://www.saatchiart.com/art/Collage-Paper-Peace/1295487/6583693/view"}, {"id": 155, "title": "Honeycomb - Mulch Series Collage", "saatchi_url": "https://www.saatchiart.com/art/Collage-Honeycomb-Mulch-Series/1295487/6583683/view"}, {"id": 156, "title": "Wild Zebra 2 - Mulch Series Collage", "saatchi_url": "https://www.saatchiart.com/art/Collage-Wild-Zebra-2-Mulch-Series/1295487/6583651/view"}, {"id": 157, "title": "Wild Zebra 1 - Mulch Series Collage", "saatchi_url": "https://www.saatchiart.com/art/Collage-Wild-Zebra-1-Mulch-Series/1295487/6583633/view"}, {"id": 158, "title": "Work Party - Mulch Series Collage", "saatchi_url": "https://www.saatchiart.com/art/Collage-Work-Party-Mulch-Series/1295487/6583609/view"}, {"id": 159, "title": "Business Mulch Collage", "saatchi_url": "https://www.saatchiart.com/art/Collage-Business-Mulch/1295487/6583595/view"}, {"id": 160, "title": "Office Work Mulch Collage", "saatchi_url": "https://www.saatchiart.com/art/Collage-Office-Work-Mulch/1295487/6583581/view"}, {"id": 161, "title": "In the Dark Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-In-The-Dark/1295487/6158223/view"}, {"id": 162, "title": "Portal 006 Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Portal-006/1295487/6158145/view"}, {"id": 163, "title": "Portal 005 Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Portal-005/1295487/6158109/view"}, {"id": 164, "title": "Portal 004 Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Portal-004/1295487/6158097/view"}, {"id": 165, "title": "Portal 003 Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Portal-003/1295487/6158079/view"}, {"id": 166, "title": "Portal 002 Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Portal-002/1295487/6158067/view"}, {"id": 167, "title": "Portal 001 Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Portal-001/1295487/6158055/view"}, {"id": 240, "title": "Blue Glacier Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Blue-Glacier/1295487/6105345/view"}, {"id": 241, "title": "Warm Glacier Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Warm-Glacier/1295487/6105343/view"}, {"id": 242, "title": "Sunset Glacier Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Sunset-Glacier/1295487/6105327/view"}, {"id": 243, "title": "Waves Painting", "saatchi_url": "https://www.saatchiart.com/art/Painting-Waves/1295487/6105315/view"}];

    console.log(`Starting scan of ${artworkList.length} items...`);
    const results = [];
    const errors = [];

    const wait = ms => new Promise(r => setTimeout(r, ms));

    for (let i = 0; i < artworkList.length; i++) {
        const item = artworkList[i];
        // console.log(`[${i + 1}/${artworkList.length}] Fetching: ${item.title}`);

        try {
            const resp = await fetch(item.saatchi_url);
            if (!resp.ok) throw new Error(`Status ${resp.status}`);
            const html = await resp.text();
            const doc = new DOMParser().parseFromString(html, 'text/html');
            const extracted = { ...item };

            // 1. Description
            const descEl = Array.from(doc.querySelectorAll('h3')).find(h => h.innerText.toUpperCase().includes('ABOUT THE ARTWORK'));
            if (descEl && descEl.nextElementSibling) {
                extracted.description = descEl.nextElementSibling.innerText.trim();
            } else {
                const metaDesc = doc.querySelector('[itemprop="description"]');
                if (metaDesc) extracted.description = metaDesc.innerText.trim();
            }

            // 2. Metadata Lines
            const extractLabel = (label) => {
                // Strategy: Find text node, go to next sibling or parent's next sibling
                const els = Array.from(doc.querySelectorAll('*'));
                const labelEl = els.find(e => e.innerText && e.innerText.trim().startsWith(label) && e.children.length < 2 && e.tagName !== 'SCRIPT');
                if (labelEl) {
                    const text = labelEl.innerText.trim();
                    if (text.length > label.length + 2) {
                        return text.replace(label, '').replace(/^:/, '').trim();
                    }
                    if (labelEl.nextElementSibling) return labelEl.nextElementSibling.innerText.trim();
                    if (labelEl.parentElement && labelEl.parentElement.nextElementSibling) return labelEl.parentElement.nextElementSibling.innerText.trim();
                }
                return null;
            };

            extracted.year = extractLabel("Year Created");
            extracted.styles = extractLabel("Styles");
            extracted.mediumsDetailed = extractLabel("Mediums");
            extracted.frame = extractLabel("Frame");
            extracted.readyToHang = extractLabel("Ready to Hang");
            extracted.packaging = extractLabel("Packaging");
            extracted.shippingFrom = extractLabel("Ships From");

            if (extracted.description && extracted.description.includes("Year Created:")) {
                extracted.description = extracted.description.split("Year Created:")[0].trim();
            }

            results.push(extracted);

        } catch (e) {
            console.error(`Failed ${item.title}:`, e);
            errors.push(item);
        }

        // Polite delay
        await wait(200);
    }

    console.log("SCRAPING COMPLETE");
    console.log(JSON.stringify(results)); // Output finding
})();
