// Run this in the WordPress Console to fetch ALL pages
(async () => {
    console.log("Fetching full inventory...");
    let allItems = [];
    let page = 1;
    let hasMore = true;

    while (hasMore) {
        try {
            const batch = await wp.apiFetch({ path: `/wp/v2/pages?per_page=100&page=${page}` });
            if (batch.length === 0) {
                hasMore = false;
            } else {
                allItems = allItems.concat(batch);
                console.log(`Fetched batch ${page}. Total items: ${allItems.length}`);
                page++;
            }
        } catch (e) {
            console.warn("End of pages or error:", e);
            hasMore = false;
        }
    }

    // Process & Filter
    // We assume Artworks typically have "Painting" in title or structure.
    // We'll capture common fields.
    const inventory = allItems.map(p => {
        // Try to find Saatchi URL in content if possible
        const content = p.content ? p.content.rendered : '';
        const saatchiMatch = content.match(/href="(https:\/\/www\.saatchiart\.com\/art\/[^"]+)"/);

        // Try to find Image URL
        const imgMatch = content.match(/src="([^"]+\.(jpg|jpeg|png))"/);

        return {
            id: p.id,
            title: p.title.rendered,
            slug: p.slug,
            link: p.link,
            saatchi_url: saatchiMatch ? saatchiMatch[1] : null,
            image_url: imgMatch ? imgMatch[1] : null
        };
    }).filter(p => !['cart', 'checkout', 'contact', 'about', 'home', 'shop', 'trade', 'blog'].includes(p.slug));
    // Basic filter for non-artwork pages, user can refine.

    console.log(`Found ${inventory.length} potential artwork pages.`);

    // Auto-Download
    const blob = new Blob([JSON.stringify(inventory, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'full_wordpress_inventory.json';
    a.click();
})();
