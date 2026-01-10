
// DEBUG PORTAL PAGE SCRIPT
(async () => {
    console.log("Debugging 'Portal' page...");

    if (typeof wp === 'undefined' || !wp.apiFetch) {
        console.error("WP API not available. Please run this in the WP Admin console.");
        return;
    }

    try {
        // 1. Find the page
        const pages = await wp.apiFetch({ path: '/wp/v2/pages?search=Portal' });
        const portalPage = pages.find(p => p.title.rendered === "Portal" || p.title.rendered === "Portal Painting");

        if (!portalPage) {
            console.error("Could not find a page named 'Portal'. Found:", pages.map(p => p.title.rendered));
            return;
        }

        console.log("Found Page ID:", portalPage.id);
        console.log("Page Link:", portalPage.link);

        // 2. Check Content
        const content = portalPage.content.rendered;
        console.log("-----------------------------------");
        console.log("CURRENT CONTENT SNIPPET (First 1000 chars):");
        console.log(content.substring(0, 1000));
        console.log("-----------------------------------");

        // 3. Analyze Image Tag
        const imgMatch = content.match(/<img[^>]+src="([^"]+)"[^>]*>/);
        if (imgMatch) {
            console.log("✅ Image Tag Found!");
            console.log("Image Source:", imgMatch[1]);

            if (imgMatch[1].includes("{{IMAGE_URL}}")) {
                console.error("❌ ERROR: Template variable {{IMAGE_URL}} was NOT replaced!");
            } else {
                console.log("Image URL seems valid format.");
            }
        } else {
            console.error("❌ ERROR: No <img> tag found in content!");
        }

        // 4. Force Update (Optional - uncomment to run)
        /*
        console.log("Attempting Force Update of Portal Page...");
        const correctUrl = "https://elliotspencermorgan.com/wp-content/uploads/2025/11/PortalPainting.jpg";
        
        // Use the snippet of the template we know works for replacing
        // We will just do a direct string replacement on the raw content if possible, 
        // or re-generate the whole thing if we had the code here. 
        // For now, let's just log.
        */

    } catch (err) {
        console.error("Debug Error:", err);
    }
})();
