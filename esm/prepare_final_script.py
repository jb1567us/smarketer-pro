import json
import base64

# 1. Read Data
with open('artwork_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 2. Read HTML Template
with open('PREMIUM_ARTWORK_LAYOUT_VERTICAL.html', 'r', encoding='utf-8') as f:
    template = f.read()

# Minify template simply
min_template = template.replace('\n', ' ').replace('  ', ' ')
# Base64 Encode
b64_tmpl = base64.b64encode(min_template.encode('utf-8')).decode('utf-8')

# 3. Define the ROBUST JavaScript Logic
js_logic = """
window.processMassBatch = async function() {
    const stats = { created: 0, updated: 0, errors: 0 };
    
    // Check if MASS_DATA exists
    if (!window.MASS_DATA) { console.error("MASS_DATA missing"); return; }

    const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

    for (const item of window.MASS_DATA) {
        try {
            // Clean title logic
            let finalTitle = item.title;
            let cleanTitle = item.cleanTitle;
            if (!cleanTitle && finalTitle.endsWith(' Painting')) {
                cleanTitle = finalTitle.replace(' Painting', '');
            }
            if (!cleanTitle) cleanTitle = finalTitle;
            
            // USE CLEAN TITLE for everything if possible
            // But we already have pages named "Caviar".
            
            let slug = item.slug; 
            let price = item.price || '990';
            let medium = item.medium || 'Oil on Canvas';

            // ... (Image check omitted for brevity in diff, assume it's same) ...
            let finalImageUrl = item.image_url;
             try {
                // Try HEAD request to see if image exists
                await fetch(finalImageUrl, { method: 'HEAD' }).then(res => {
                    if (!res.ok) throw new Error('404');
                });
            } catch (e) {
                 // fallback logic: replace _ with -
                 // const hyphenUrl = finalImageUrl.replace(/_/g, '-');
                 console.warn(`Image might be missing for ${finalTitle}: ${finalImageUrl}`);
            }

            // VISUAL TAGS MAP (Manual Overrides from Visual Analysis)
            // MUST INCLUDE: Style, Color, Pattern, Size
            const visualTags = {
                'Caviar': 'Monochrome, Black & White, Cellular, Organic Pattern, High Contrast, Intricate, Ink, Contemporary Art, Abstract, Large, Square',
                'Portal': 'Red, Indigo, Abstract, Expressionism, Center Focus, Cosmic, Void, Large, Square, Painting, Minimalist, Multicolor',
                'Meeting in the Middle': 'Geometric, Structure, Balance, Architectural, Line Work, Harmony, Warm Tones, Abstract, Large, Square, Beige, Black',
                'Convergence': 'Pattern, Rhythm, Flow, Kinetic, Detailed, Movement, Organic Lines, Intricate, Abstract, Monochrome, Black & White, Large, Square',
                'Sheet Music': 'Lyrical, Flowing, Calligraphic, Black & White, Musical, Gestural, Rhythm, Ink, Abstract, Pattern, Large, Square',
                'Finger print': 'Identity, Biomorphic, Whorls, Organic, Unique, Personal, Line Work, Black & White, Monochrome, Large, Square, Abstract',
                'Puzzled': 'Geometric, Interlocking, Maze, Complexity, Abstract Puzzle, Linear, Problem Solving, Structure, Black & White, Monochrome, Abstract, Large, Square',
                'Red Planet': 'Red, Mars, Warm Tones, Texture, Planetary, Bold, Abstract, Expressionism, Large, Square, Pattern',
                'Portal 2': 'Blue, Deep, Series, Depth, Abstract, Minimalist, Void, Atmospheric, Center Focus, Large, Square, Painting',
                'Abstract Landscape': 'Landscape, Abstract, Horizontal, Nature, Earth Tones, Atmospheric, Green, Brown, Large, Square',
                'Self portrait 1': 'Abstract Portrait, Identity, Psychological, Line Work, Figurative Abstract, Self, Black & White, Monochrome, Large, Square',
            };

            // SMART TAGS GENERATOR
            const generateSmartTags = (i, safeTitle) => {
                let t = new Set();
                const titleForSearch = safeTitle || i.title;

                // 1. ADD VISUAL MAP TAGS FIRST (If available)
                if (visualTags[titleForSearch]) {
                     visualTags[titleForSearch].split(',').forEach(s => t.add(s.trim()));
                } else {
                    // Check Case Insensitive
                    const titleKey = Object.keys(visualTags).find(k => k.toLowerCase() === titleForSearch.toLowerCase());
                    if (titleKey) visualTags[titleKey].split(',').forEach(s => t.add(s.trim()));
                }

                // 2. ALWAYS CALCULATE SIZE & FORMAT (User requirement: Size must be present)
                const w = parseInt(i.width || 0);
                const h = parseInt(i.height || 0);
                if (w >= 48 || h >= 48) { t.add('Large'); t.add('Statement Piece'); t.add('Oversized'); }
                if (w > 0 && w === h) t.add('Square');
                else if (w > h) t.add('Landscape Format');
                else if (h > w) t.add('Portrait Format');

                // 3. BASE TAGS (Styles & Medium)
                if (i.styles) i.styles.split(',').forEach(s => t.add(s.trim()));
                if (i.medium) t.add(i.medium);
                t.add('Contemporary Art');
                t.add('Modern');

                // 4. COLOR & THEME INFERENCE (from Title)
                const titleLower = titleForSearch.toLowerCase();
                
                if (titleLower.includes('red') || titleLower.includes('planet') || titleLower.includes('mars')) { t.add('Red'); t.add('Warm Tones'); }
                if (titleLower.includes('gold') || titleLower.includes('sun')) { t.add('Gold'); t.add('Yellow'); t.add('Metallic'); t.add('Shimmer'); t.add('Series'); }
                if (titleLower.includes('series')) { t.add('Collection'); t.add('Continuity'); }
                if (titleLower.includes('blue') || titleLower.includes('lake') || titleLower.includes('sea') || titleLower.includes('beach') || titleLower.includes('water') || titleLower.includes('portal')) { t.add('Blue'); t.add('Cool Tones'); }
                if (titleLower.includes('green') || titleLower.includes('park') || titleLower.includes('garden')) { t.add('Green'); t.add('Nature'); }
                if (titleLower.includes('caviar')) { t.add('Black'); t.add('Dark'); t.add('Monochrome'); }
                if (titleLower.includes('sheet music')) { t.add('Black & White'); t.add('Music'); }
                if (titleLower.includes('finger print')) { t.add('Identity'); t.add('Abstract'); }
                if (titleLower.includes('puzzled')) { t.add('Geometric'); t.add('Complexity'); }

                return Array.from(t).join(', ');
            };

            let tags = generateSmartTags(item, cleanTitle);

            // COMPILE TEMPLATE
            let content = window.layoutTemplate
                .replace(/{{TITLE}}/g, cleanTitle) // Use Clean Title in Template!
                .replace(/{{IMAGE_URL}}/g, finalImageUrl) 
                .replace(/{{PRICE}}/g, price)
                .replace(/{{MEDIUM}}/g, medium)
                .replace(/{{DESCRIPTION}}/g, item.long_description || `Original ${medium} painting by Elliot Spencer Morgan. Signed and delivered with a Certificate of Authenticity.`)
                .replace(/{{YEAR}}/g, item.year || '2024')
                .replace(/{{STYLES}}/g, item.styles || 'Abstract')
                .replace(/{{MEDIUMS_DETAILED}}/g, item.mediumsDetailed || medium)
                .replace(/{{FRAME}}/g, item.frame || 'Gallery Wrapped')
                .replace(/{{PACKAGING}}/g, item.packaging || 'Ships Rolled in a Tube')
                .replace(/{{SHIPPING}}/g, item.shippingFrom || 'United States')
                .replace(/{{DIMENSIONS}}/g, `${item.width} W x ${item.height} H x 1.5 D in`)
                .replace(/{{SAATCHI_URL}}/g, item.saatchi_url)
                .replace(/{{TAGS}}/g, tags);

            console.log(`Processing: ${cleanTitle}`);

            // SEARCH FOR EXISTING PAGE (Status=ANY to find drafts)
            const existingPages = await wp.apiFetch({ path: `/wp/v2/pages?search=${encodeURIComponent(cleanTitle)}&per_page=5&status=any` });
            let pageIdToUpdate = null;
            
            if (existingPages && existingPages.length > 0) {
                 // Fuzzy match: exact clean title OR exact full title
                 const match = existingPages.find(p => 
                    p.title.rendered.toLowerCase() === cleanTitle.toLowerCase() || 
                    p.title.rendered.toLowerCase() === finalTitle.toLowerCase()
                 );
                 if (match) pageIdToUpdate = match.id;
            }

            if (pageIdToUpdate) {
                console.log(`Updating existing page ${pageIdToUpdate}...`);
                await wp.apiFetch({
                    path: `/wp/v2/pages/${pageIdToUpdate}`,
                    method: 'PUT',
                    data: {
                        content: content
                    }
                });
                stats.updated++;
            } else {
                console.log(`Creating new page...`);
                await wp.apiFetch({
                    path: '/wp/v2/pages',
                    method: 'POST',
                    data: {
                        title: finalTitle,
                        content: content,
                        status: 'publish',
                        slug: slug
                    }
                });
                stats.created++;
            }

        } catch (err) {
            console.error(`Error processing ${item.title}:`, err);
            stats.errors++;
        }

        // Wait to avoid rate limits
        await delay(500);
    }
    
    console.log("Batch Complete. Created:", stats.created, "Updated:", stats.updated, "Errors:", stats.errors);
    alert("Batch Complete!");
}
"""

# 4. Construct Final JS File
manual_js_content = f"""
// MASS MIGRATION SCRIPT - MANUAL EXECUTION
// Generated by prepare_final_script.py

// 1. SETUP (Template)
// Decode Base64 Template
window.layoutTemplate = new TextDecoder().decode(Uint8Array.from(atob("{b64_tmpl}"), c => c.charCodeAt(0)));

// 2. LOGIC
{js_logic}

// 3. DATA
window.MASS_DATA = {json.dumps(data)};

// 4. EXECUTE
(async () => {{
    console.log("Starting MASS MIGRATION for " + window.MASS_DATA.length + " items...");
    if (typeof processMassBatch !== 'function') {{
        console.error("processMassBatch is not defined!");
        return;
    }}
    await processMassBatch();
}})();
"""

with open('mass_migration_full.js', 'w', encoding='utf-8') as f:
    f.write(manual_js_content.strip())

print(f"✅ Generated mass_migration_full.js with {len(data)} items and NEW METADATA LOGIC.")
