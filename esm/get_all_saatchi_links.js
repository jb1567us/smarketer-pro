
(function () {
    console.log("Scanning all posts for Saatchi links...");

    if (typeof wp === 'undefined' || !wp.data || !wp.apiFetch) {
        return "wp.data not available";
    }

    async function getAllPosts() {
        let allPosts = [];
        let page = 1;
        let complete = false;

        while (!complete) {
            try {
                // Fetch 100 at a time
                const posts = await wp.apiFetch({ path: `/wp/v2/posts?per_page=100&page=${page}` });
                if (posts.length === 0) {
                    complete = true;
                } else {
                    allPosts = allPosts.concat(posts);
                    page++;
                    console.log(`Fetched page ${page - 1} (${posts.length} items)...`);
                }
            } catch (err) {
                console.error("Error fetching page " + page, err);
                complete = true;
            }
        }
        return allPosts;
    }

    getAllPosts().then(posts => {
        const payload = posts.map(p => {
            // Extract Saatchi URL
            const urlMatch = p.content.rendered.match(/href="(https:\/\/www\.saatchiart\.com\/art\/[^"]+)"/);
            // Extract Image URL
            const imgMatch = p.content.rendered.match(/src="([^"]+)"/);

            return {
                id: p.id,
                title: p.title.rendered,
                slug: p.slug,
                saatchi_url: urlMatch ? urlMatch[1] : null,
                image_url: imgMatch ? imgMatch[1] : null,
                date: p.date
            };
        }).filter(item => item.saatchi_url); // Only keep ones with valid Saatchi links

        console.log(`Found ${payload.length} artworks with Saatchi links.`);
        console.log("JSON_START");
        console.log(JSON.stringify(payload, null, 2));
        console.log("JSON_END");
    });
})();
