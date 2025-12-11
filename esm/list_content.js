
(function () {
    console.log("Fetching all pages and posts...");

    if (typeof wp === 'undefined' || !wp.data) {
        return "wp.data not available";
    }

    const pagesResponse = wp.data.select('core').getEntityRecords('postType', 'page', { per_page: 100 });
    const postsResponse = wp.data.select('core').getEntityRecords('postType', 'post', { per_page: 100 });

    // We need to wait for resolution, but in this console context we might get null initially if not loaded.
    // However, if we just triggered it, it might trigger a fetch.
    // A better way in automation is to just return what we have or use a promise if possible (but browser tool might not await promises returned from eval)

    // Let's try to return the list if available, otherwise simplified status
    if (pagesResponse && postsResponse) {
        const pages = pagesResponse.map(p => ({ id: p.id, title: p.title.rendered, link: p.link }));
        const posts = postsResponse.map(p => ({ id: p.id, title: p.title.rendered, link: p.link }));
        return JSON.stringify({ pages, posts }, null, 2);
    } else {
        return "Loading records... run again in a few seconds";
    }
})();
