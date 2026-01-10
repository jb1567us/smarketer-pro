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
            function generateSmartTags(i) {
                const t = new Set();
                const titleForSearch = i.cleanTitle || i.title;
                const titleLower = titleForSearch.toLowerCase();
                
                // 1. STYLE & MEDIUM (From Metadata)
                if (i.styles) {
                    i.styles.split(',').forEach(s => t.add(s.trim()));
                }
                if (i.mediumsDetailed) {
                     i.mediumsDetailed.split(',').forEach(s => t.add(s.trim()));
                } else if (i.medium) {
                    t.add(i.medium);
                }

                // 2. DIMENSION Based Tags
                const w = parseFloat(i.width || 0);
                const h = parseFloat(i.height || 0);
                if (w > 0 && h > 0) {
                    if (w >= 48 || h >= 48) { t.add('Large'); t.add('Statement Piece'); t.add('Oversized'); }
                    if (Math.abs(w - h) < 1) t.add('Square'); // Tolerance for float
                    else if (w > h) t.add('Landscape Format');
                    else if (h > w) t.add('Portrait Format');
                }

                 // 3. ARTWORK TYPE DETECTION (Robust)
                let typeDetected = false;
                const typeKeywords = ['painting', 'sculpture', 'collage', 'drawing', 'print', 'digital art', 'photography', 'installation'];
                
                typeKeywords.forEach(type => {
                    if (titleLower.includes(type)) {
                        t.add(type.charAt(0).toUpperCase() + type.slice(1));
                        typeDetected = true;
                    }
                });
                
                // Fallback type if possible
                if (!typeDetected) {
                    if (i.medium && i.medium.toLowerCase().includes('canvas')) t.add('Painting');
                    else if (i.medium && i.medium.toLowerCase().includes('paper')) t.add('Work on Paper');
                    else t.add('Painting'); // Default
                }

                 // 4. COLOR & THEME INFERENCE (Expanded)
                const colorMap = {
                    'red': ['Red', 'Warm Tones', 'Bold'],
                    'crimson': ['Red', 'Deep Red'],
                    'blue': ['Blue', 'Cool Tones', 'Calm'],
                    'navy': ['Blue', 'Dark'],
                    'turquoise': ['Turquoise', 'Blue-Green', 'Vibrant'],
                    'gold': ['Gold', 'Metallic', 'Yellow', 'Warm Tones', 'Luxury'],
                    'yellow': ['Yellow', 'Bright', 'Sunny'],
                    'green': ['Green', 'Nature', 'Organic'],
                    'purple': ['Purple', 'Royalty', 'Mysterious'],
                    'black': ['Black', 'Dark', 'Monochrome', 'Minimalist'],
                    'white': ['White', 'Light', 'Minimalist'],
                    'silver': ['Silver', 'Metallic', 'Cool Tones'],
                    'orange': ['Orange', 'Citrus', 'Warm Tones'],
                    'pink': ['Pink', 'Soft', 'Playful'],
                    'brown': ['Brown', 'Earth Tones', 'Natural'],
                    'grey': ['Grey', 'Neutral'],
                    'gray': ['Grey', 'Neutral']
                };

                Object.keys(colorMap).forEach(key => {
                    if (titleLower.includes(key)) {
                        colorMap[key].forEach(tag => t.add(tag));
                    }
                });

                // Theme keywords
                if (titleLower.includes('lake') || titleLower.includes('sea') || titleLower.includes('beach') || titleLower.includes('water') || titleLower.includes('ocean')) { t.add('Water'); t.add('Nature'); t.add('Landscape'); }
                if (titleLower.includes('mountain') || titleLower.includes('hill') || titleLower.includes('valley')) { t.add('Mountain'); t.add('Landscape'); t.add('Nature'); }
                if (titleLower.includes('tree') || titleLower.includes('forest') || titleLower.includes('plant') || titleLower.includes('flower') || titleLower.includes('bloom')) { t.add('Botanical'); t.add('Nature'); t.add('Floral'); }
                if (titleLower.includes('city') || titleLower.includes('urban') || titleLower.includes('building') || titleLower.includes('street')) { t.add('Urban'); t.add('Cityscape'); t.add('Architecture'); }
                if (titleLower.includes('abstract')) { t.add('Abstract'); t.add('Non-Objective'); }
                if (titleLower.includes('geometric') || titleLower.includes('shape') || titleLower.includes('cube') || titleLower.includes('circle')) { t.add('Geometric'); t.add('Structured'); }
                if (titleLower.includes('portrait') || titleLower.includes('face') || titleLower.includes('figure')) { t.add('Portrait'); t.add('Figurative'); }
                if (titleLower.includes('animal') || titleLower.includes('bird') || titleLower.includes('dog') || titleLower.includes('cat') || titleLower.includes('fish')) { t.add('Animals'); t.add('Wildlife'); }
                if (titleLower.includes('music') || titleLower.includes('song') || titleLower.includes('dance')) { t.add('Music'); t.add('Rhythm'); t.add('Performing Arts'); }

                // 5. Title Keywords (Smart Extraction - excluding stop words)
                const stopWords = ['a', 'an', 'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'series', 'painting', 'sculpture', 'collage', '001', '002', '003', '004', '005', '006', '007', '008', '009', '010', '011', '1', '2', '3', '4', '5', '6', '7', '8', '9'];
                titleLower.split(/[^a-z0-9]+/).forEach(word => {
                    if (word.length > 3 && !stopWords.includes(word)) {
                        // Capitalize first letter
                        t.add(word.charAt(0).toUpperCase() + word.slice(1));
                    }
                });

                // 6. DETECTED COLORS (From Image Analysis)
                if (i.detected_colors && Array.isArray(i.detected_colors)) {
                    i.detected_colors.forEach(c => t.add(c));
                    if (i.detected_colors.length > 3) t.add('Colorful');
                    if (i.detected_colors.length > 1) t.add('Multicolored');
                }

                // 7. Base Tags
                t.add('Contemporary Art');
                t.add('Fine Art');
                t.add('Elliot Spencer Morgan');

                return Array.from(t).join(', ');
            }

            let tags = generateSmartTags(item);

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

            // 1. Try by WordPress ID (Safest)
            if (item.wordpress_id) {
                console.log(`Checking ID ${item.wordpress_id}...`);
                try {
                     const directCheck = await wp.apiFetch({ path: `/wp/v2/pages/${item.wordpress_id}` });
                     if (directCheck && directCheck.id) {
                         pageIdToUpdate = directCheck.id;
                     }
                } catch (e) {
                    console.log(`ID ${item.wordpress_id} not found, falling back to search.`);
                }
            }

            // 2. Fallback to Search (if no ID or ID failed)
            if (!pageIdToUpdate) {
                // Search for pages with similar title
                const existingPages = await wp.apiFetch({ path: `/wp/v2/pages?search=${encodeURIComponent(cleanTitle)}&per_page=10&status=any` });
                
                if (existingPages && existingPages.length > 0) {
                     // PRIORITIZE SLUG MATCH
                     const slugMatch = existingPages.find(p => p.slug === slug);
                     if (slugMatch) {
                         pageIdToUpdate = slugMatch.id;
                         console.log(`Matched by Slug: ${slug}`);
                     } else {
                         // Fallback to Accurate Title Match
                         const titleMatch = existingPages.find(p => 
                            p.title.rendered.toLowerCase().trim() === cleanTitle.toLowerCase().trim() || 
                            p.title.rendered.toLowerCase().trim() === finalTitle.toLowerCase().trim() ||
                            p.title.rendered.includes(cleanTitle) // Looser check?
                         );
                         if (titleMatch) { 
                            pageIdToUpdate = titleMatch.id;
                            console.log(`Matched by Title: ${titleMatch.title.rendered}`);
                         }
                     }
                }
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
