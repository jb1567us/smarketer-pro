// UNPUBLISH MISSING ARTWORK SCRIPT
// Sets pages to 'draft' if their image is missing from the verified file list.

(async () => {
    console.log("🚫 Identifying pages with missing images to unpublish...");

    if (typeof wp === 'undefined' || !wp.apiFetch) {
        console.error("❌ Run this in WordPress Admin console!");
        return;
    }

    // List of titles confimed MISSING from 2025/11 uploads list
    const missingTitles = [
        "A Day at the Lake",
        "A day at the park",
        "A day at the beach",
        "Gold Series 007",
        "Gold Series 008",
        "Gold Series 009",
        "Gold Series 010",
        "Gold Series 011"
    ];

    let unpublishedCount = 0;

    for (const title of missingTitles) {
        try {
            // Find the page
            const pages = await wp.apiFetch({
                path: `/wp/v2/pages?search=${encodeURIComponent(title)}&per_page=1`
            });

            if (pages.length > 0) {
                const page = pages[0];

                // Confirm it's the right page (exact title match or with Painting suffix)
                if (page.title.rendered.includes(title)) {

                    // Update status to draft
                    await wp.apiFetch({
                        path: `/wp/v2/pages/${page.id}`,
                        method: 'POST',
                        data: {
                            status: 'draft'
                        }
                    });

                    console.log(`✅ Unpublished: "${page.title.rendered}" (ID: ${page.id})`);
                    unpublishedCount++;
                }
            } else {
                console.log(`⚠️ Page not found (already deleted?): "${title}"`);
            }

        } catch (err) {
            console.error(`❌ Error unpublishing "${title}":`, err.message);
        }
    }

    console.log("=========================================");
    console.log(`SUMMARY: Unpublished ${unpublishedCount} pages.`);
    console.log("These pages are now drafts and hidden from the public site.");
    console.log("You can publish them later when you verify the images.");
    console.log("=========================================");

})();
