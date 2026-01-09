// CLEANUP AND FIX SCRIPT
// This will delete old conflicting pages and create fresh ones with correct content

(async () => {
    console.log("🔧 Starting cleanup and fix...\n");

    if (typeof wp === 'undefined' || !wp.apiFetch) {
        console.error("❌ Run this in WordPress Admin console!");
        return;
    }

    // Step 1: Find and delete ALL pages with "lakePainting" or "portal-abstract" slugs (old pages)
    console.log("Step 1: Finding old conflicting pages...");

    const allPages = await wp.apiFetch({ path: '/wp/v2/pages?per_page=100' });
    const oldPages = allPages.filter(p =>
        p.slug.includes('Painting') ||
        p.slug === 'portal-abstract' ||
        p.slug.includes('_')  // Old slug format with underscores
    );

    console.log(`Found ${oldPages.length} old pages to delete:`);
    for (const page of oldPages) {
        console.log(`  - "${page.title.rendered}" (${page.slug})`);
    }

    if (oldPages.length > 0) {
        const confirm = window.confirm(`Delete ${oldPages.length} old pages? Click OK to proceed.`);
        if (!confirm) {
            console.log("❌ Cancelled by user");
            return;
        }

        for (const page of oldPages) {
            try {
                await wp.apiFetch({
                    path: `/wp/v2/pages/${page.id}`,
                    method: 'DELETE'
                });
                console.log(`  ✅ Deleted: ${page.title.rendered}`);
            } catch (err) {
                console.error(`  ❌ Failed to delete ${page.title.rendered}:`, err.message);
            }
        }
    }

    console.log("\n✅ Cleanup complete!");
    console.log("\n🚀 Now run mass_migration_full.js to create fresh pages.");
    console.log("   The pages will now display correctly!");

})();
