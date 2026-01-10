// CLEANUP DUPLICATES SCRIPT (ROBUST VERSION)
// Run this in console to delete pages with "-2" slugs created by accident
// Includes delays to prevent server errors.

(async () => {
    console.log("Checking for duplicate '-2' pages...");

    try {
        // 1. Fetch all pages
        // Fetching 100 should be enough for now.
        const allPages = await wp.apiFetch({ path: '/wp/v2/pages?per_page=100' });

        // 2. Identify duplicates
        // Look for slugs ending in -2 OR -3 just in case
        const duplicates = allPages.filter(p => p.slug.match(/-\d+$/) && (p.slug.includes('caviar') || p.slug.includes('gold') || p.slug.includes('day')));

        if (duplicates.length === 0) {
            console.log("✅ No duplicate pages found.");
            return;
        }

        console.log(`⚠️ Found ${duplicates.length} duplicate pages:`);
        duplicates.forEach(p => console.log(`   - ${p.title.rendered} (slug: ${p.slug})`));

        // Helper for delay
        const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

        // 3. Delete them?
        if (confirm(`Found ${duplicates.length} duplicates. Delete them?`)) {

            for (const p of duplicates) {
                console.log(`Deleting ${p.title.rendered} (ID: ${p.id})...`);

                try {
                    await wp.apiFetch({
                        path: `/wp/v2/pages/${p.id}`,
                        method: 'DELETE'
                    });
                    console.log(`✅ Deleted.`);
                } catch (err) {
                    console.error(`❌ Failed to delete ${p.title.rendered}:`, err);
                }

                // WAIT 2 SECONDS to be gentle to the server
                await wait(2000);
            }
            console.log("✅ Cleanup complete.");
        } else {
            console.log("Cancelled.");
        }

    } catch (e) {
        console.error("Error fetching pages:", e);
    }

})();
