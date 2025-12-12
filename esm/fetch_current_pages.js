// Fetch ALL WordPress pages and update artwork_data.json with correct links/slugs
(async function () {
    console.log("Fetching all WordPress pages to get correct slugs...");

    if (typeof wp === 'undefined' || !wp.data || !wp.apiFetch) {
        return console.error("wp.data not available. Run in WordPress Admin.");
    }

    // Fetch all pages
    let allPages = [];
    let page = 1;
    let complete = false;

    while (!complete) {
        try {
            const pages = await wp.apiFetch({
                path: `/wp/v2/pages?per_page=100&page=${page}`
            });

            if (pages.length === 0) {
                complete = true;
            } else {
                allPages = allPages.concat(pages);
                page++;
                console.log(`Fetched page ${page - 1} (${pages.length} items)...`);
            }
        } catch (err) {
            console.error("Error fetching page " + page, err);
            complete = true;
        }
    }

    console.log(`\\nTotal pages found: ${allPages.length}`);

    // Extract just the info we need
    const pageData = allPages.map(p => ({
        id: p.id,
        title: p.title.rendered,
        slug: p.slug,
        link: p.link,
        type: p.type
    }));

    // Output as JSON
    console.log("\\n=== COPY THIS JSON ===");
    console.log(JSON.stringify(pageData, null, 2));
    console.log("=== END JSON ===");

    // Auto-download
    const blob = new Blob([JSON.stringify(pageData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'wordpress_pages_current.json';
    a.click();

    console.log("\\nDownloaded as wordpress_pages_current.json");
})();
