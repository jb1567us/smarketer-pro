// Run this in the WordPress Console to fetch ALL pages AND posts
(async () => {
    console.log("Fetching full inventory (pages and posts)...");
    let allItems = [];
    let page = 1;
    let hasMore = true;

    // Fetch Pages
    while (hasMore) {
        try {
            const batch = await wp.apiFetch({ path: `/wp/v2/pages?per_page=100&page=${page}&status=any&orderby=id&order=asc` });
            if (batch.length === 0) {
                hasMore = false;
            } else {
                allItems = allItems.concat(batch);
                console.log(`Fetched page batch ${page}. Total items: ${allItems.length}`);
                page++;
            }
        } catch (e) {
            console.warn("End of pages or error:", e);
            hasMore = false;
        }
    }

    // Fetch Posts (Just in case some artworks are posts)
    page = 1;
    hasMore = true;
    while (hasMore) {
        try {
            const batch = await wp.apiFetch({ path: `/wp/v2/posts?per_page=100&page=${page}&status=any&orderby=id&order=asc` });
            if (batch.length === 0) {
                hasMore = false;
            } else {
                allItems = allItems.concat(batch);
                console.log(`Fetched post batch ${page}. Total items: ${allItems.length}`);
                page++;
            }
        } catch (e) {
            console.warn("End of posts or error:", e);
            hasMore = false;
        }
    }

    // Process & Filter
    const inventory = allItems.map(p => {
        const content = p.content ? p.content.rendered : '';
        const saatchiMatch = content.match(/href="(https:\/\/www\.saatchiart\.com\/art\/[^"]+)"/);
        const imgMatch = content.match(/src="([^"]+\.(jpg|jpeg|png))"/);

        return {
            id: p.id,
            title: p.title.rendered,
            slug: p.slug,
            link: p.link,
            saatchi_url: saatchiMatch ? saatchiMatch[1] : null,
            image_url: imgMatch ? imgMatch[1] : null,
            type: p.type // 'page' or 'post'
        };
    }).filter(p => !['cart', 'checkout', 'contact', 'about', 'home', 'shop', 'trade', 'blog', 'hello-world'].includes(p.slug));

    console.log(`Found ${inventory.length} potential artwork items.`);

    const blob = new Blob([JSON.stringify(inventory, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'full_wordpress_inventory_all.json';
    a.click();
})();
