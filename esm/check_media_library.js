// MEDIA LIBRARY AUDIT SCRIPT
// Run this in your WordPress Admin Console to see EXACTLY what filenames WordPress has.

(async () => {
    console.log("📂 Scanning Media Library for 'A Day at the Lake'...");

    if (typeof wp === 'undefined' || !wp.apiFetch) {
        console.error("❌ Run this in WordPress Admin console!");
        return;
    }

    try {
        // Fetch media items matching "lake" and "portal"
        const mediaItems = await wp.apiFetch({
            path: '/wp/v2/media?search=lake&per_page=20'
        });

        console.log(`\nFound ${mediaItems.length} media items matching 'lake':`);
        console.log("==================================================");

        mediaItems.forEach(item => {
            console.log(`\n🖼️  ID: ${item.id}`);
            console.log(`    Title: "${item.title.rendered}"`);
            console.log(`    Source URL: ${item.source_url}`);

            // Extract the filename part
            const filename = item.source_url.split('/').pop();
            console.log(`    Filename: [ ${filename} ]`);

            console.log(`    Media Details:`);
            if (item.media_details && item.media_details.sizes) {
                const sizes = Object.keys(item.media_details.sizes).join(', ');
                console.log(`      Sizes generated: ${sizes}`);
            }
        });

        console.log("\n==================================================");
        console.log("Compare the 'Filename' above with what we have in the script:");
        console.log("Target: A-Day-at-the-LakePainting.jpg");

    } catch (err) {
        console.error("Error fetching media:", err);
    }
})();
