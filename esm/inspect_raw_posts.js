
(function () {
    console.log("Fetching sample posts to inspect content structure...");

    if (typeof wp === 'undefined' || !wp.data || !wp.apiFetch) {
        return "wp.data not available";
    }

    // Fetch 5 random posts (excluding the ones we already processed)
    // We'll just fetch the latest 10 and pick ones that don't have our new pages
    wp.apiFetch({ path: '/wp/v2/posts?per_page=10' }).then(posts => {
        const samples = posts.map(p => ({
            id: p.id,
            title: p.title.rendered,
            slug: p.slug,
            // Capture the raw content to see if price/dims are hidden there
            content_snippet: p.content.rendered.substring(0, 1000),
            // Check custom fields if any exposed in API
            meta: p.meta
        }));
        console.log(JSON.stringify(samples, null, 2));
    });
})();
