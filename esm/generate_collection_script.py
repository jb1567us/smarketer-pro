import json

# Load collections data
with open(r'C:\sandbox\esm\collections_data.json', 'r', encoding='utf-8') as f:
    collections = json.load(f)

# Load artwork data to get updated links
with open(r'C:\sandbox\esm\artwork_data.json', 'r', encoding='utf-8') as f:
    artworks = json.load(f)

# Create lookup by saatchi_url
artworks_by_url = {a['saatchi_url']: a for a in artworks if a.get('saatchi_url')}

# Update collections with latest artwork data
for coll_key, coll_data in collections.items():
    for artwork in coll_data['artworks']:
        url = artwork.get('saatchi_url')
        if url and url in artworks_by_url:
            # Update with latest data from artwork_data.json
            latest = artworks_by_url[url]
            artwork.update(latest)

# Save updated collections
with open(r'C:\sandbox\esm\collections_data.json', 'w', encoding='utf-8') as f:
    json.dump(collections, f, indent=2, ensure_ascii=False)

print("Updated collections with latest artwork data")

# Now generate the script
js_script = '''
// Create Collection Pages - UPDATED WITH ALL LINKS
(async function() {
    console.log("Creating collection pages...");
    
    if (typeof wp === 'undefined' || !wp.data || !wp.apiFetch) {
        return console.error("wp.data not available. Run in WordPress Admin.");
    }

    const collections = ''' + json.dumps(collections, indent=4) + ''';
    
    let created = 0;
    let updated = 0;
    let errors = 0;

    for (const [slug, collection] of Object.entries(collections)) {
        console.log(`\\nProcessing: ${collection.title}`);
        
        // Build artwork cards HTML
        let artworkCards = '';
        collection.artworks.forEach(artwork => {
            const dims = artwork.dimensions || `${artwork.width || '?'} W x ${artwork.height || '?'} H in`;
            const medium = artwork.mediumsDetailed || artwork.medium || 'Mixed Media';
            
            // Build WordPress link using slug (all pages should exist now)
            let link = '';
            if (artwork.link && artwork.link.includes('elliotspencermorgan.com')) {
                link = artwork.link;
            } else if (artwork.slug) {
                link = `/${artwork.slug}`;
            } else {
                // Generate slug from title
                const slug = artwork.title.toLowerCase()
                    .replace(/[^a-z0-9]+/g, '-')
                    .replace(/^-|-$/g, '');
                link = `/${slug}`;
            }
            
            const image = artwork.image_url || '';
            
            artworkCards += `
        <div class="artwork-card" style="text-align: center;">
            <a href="${link}">
                <img src="${image}" alt="${artwork.title}" style="width: 100%; height: auto; margin-bottom: 10px;">
            </a>
            <h3 style="font-size: 18px; margin: 10px 0;"><a href="${link}" style="text-decoration: none; color: #000;">${artwork.title}</a></h3>
            <p class="details" style="font-size: 14px; color: #666;">${dims} | ${medium}</p>
        </div>`;
        });
        
        // Build related collections links
        const relatedLinks = Object.values(collections)
            .filter(c => c.slug !== collection.slug)
            .map(c => `<li><a href="/${c.slug}">${c.title}</a></li>`)
            .join('\\n            ');
        
        // Build full HTML
        const html = `
<div class="collection-page">
    <h1>${collection.title}</h1>
    <p class="collection-intro">${collection.description}</p>
    
    <div class="collection-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 30px; margin: 40px 0;">
        ${artworkCards}
    </div>
    
    <div class="collection-cta" style="text-align: center; margin: 60px 0; padding: 40px; background: #f5f5f5;">
        <h2>Questions About This Collection?</h2>
        <p>I'd love to help you find the perfect piece for your space.</p>
        <p><a href="/contact" style="display: inline-block; background: #000; color: #fff; padding: 12px 30px; text-decoration: none; margin: 10px;">Get in Touch</a></p>
        <p>Interior Designer? <a href="/trade">View our Trade Program</a></p>
    </div>
    
    <div class="related-collections" style="margin: 40px 0;">
        <h2>Explore More Collections</h2>
        <ul style="list-style: none; padding: 0;">
            ${relatedLinks}
        </ul>
    </div>
</div>`;

        try {
            // Check if page exists
            const existing = await wp.apiFetch({ 
                path: `/wp/v2/pages?slug=${collection.slug}` 
            });
            
            if (existing && existing.length > 0) {
                // Update existing
                await wp.apiFetch({
                    path: `/wp/v2/pages/${existing[0].id}`,
                    method: 'POST',
                    data: {
                        content: html,
                        status: 'publish'
                    }
                });
                updated++;
                console.log(`✅ Updated: ${collection.title}`);
            } else {
                // Create new
                await wp.apiFetch({
                    path: '/wp/v2/pages',
                    method: 'POST',
                    data: {
                        title: collection.title,
                        content: html,
                        slug: collection.slug,
                        status: 'publish'
                    }
                });
                created++;
                console.log(`✅ Created: ${collection.title}`);
            }
        } catch (err) {
            errors++;
            console.error(`❌ Failed: ${collection.title}`, err);
        }
    }
    
    console.log(`\\n=== COMPLETE ===`);
    console.log(`Created: ${created}`);
    console.log(`Updated: ${updated}`);
    console.log(`Errors: ${errors}`);
})();
'''

# Save the script
with open(r'C:\sandbox\esm\create_collection_pages.js', 'w', encoding='utf-8') as f:
    f.write(js_script)

print("Generated create_collection_pages.js with updated links")
