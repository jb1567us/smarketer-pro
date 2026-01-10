// DEBUG: Find all Portal-related pages
(async () => {
    console.log("Searching for all pages with 'Portal' in the name...");

    if (typeof wp === 'undefined' || !wp.apiFetch) {
        console.error("WP API not available. Run this in WordPress Admin console.");
        return;
    }

    try {
        // Search for all pages containing "portal"
        const pages = await wp.apiFetch({
            path: '/wp/v2/pages?search=portal&per_page=100'
        });

        console.log(`Found ${pages.length} page(s) with 'Portal':`);
        console.log("=====================================");

        pages.forEach((page, index) => {
            console.log(`\n${index + 1}. "${page.title.rendered}"`);
            console.log(`   ID: ${page.id}`);
            console.log(`   Slug: ${page.slug}`);
            console.log(`   URL: ${page.link}`);
            console.log(`   Status: ${page.status}`);
            console.log(`   Modified: ${page.modified}`);

            // Check if image exists in content
            const hasImage = page.content.rendered.includes('<img');
            const imageUrl = page.content.rendered.match(/src="([^"]+)"/);
            console.log(`   Has Image: ${hasImage ? '✅' : '❌'}`);
            if (imageUrl) {
                console.log(`   Image URL: ${imageUrl[1]}`);
            }
        });

        console.log("\n=====================================");
        console.log("RECOMMENDATION:");
        console.log("If you see multiple 'Portal' pages, delete the OLD one(s) from WordPress admin.");
        console.log("The correct one should have:");
        console.log("  - Slug: 'portal' or 'portal-painting'");
        console.log("  - Image URL containing: elliotspencermorgan.com");

    } catch (err) {
        console.error("Error:", err);
    }
})();
