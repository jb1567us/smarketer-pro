// ALL-IN-ONE: Cleanup old pages + Re-migrate with correct content
(async () => {
    console.log("🔧 STEP 1/2: Deleting old conflicting pages...\n");

    if (typeof wp === 'undefined' || !wp.apiFetch) {
        console.error("❌ Run this in WordPress Admin console!");
        return;
    }

    // Delete old pages with bad slugs
    try {
        const allPages = await wp.apiFetch({ path: '/wp/v2/pages?per_page=100' });
        const oldPages = allPages.filter(p =>
            p.slug.includes('Painting') ||
            p.slug === 'portal-abstract' ||
            p.slug.includes('_')
        );

        console.log(`Found ${oldPages.length} old pages to delete`);

        for (const page of oldPages) {
            await wp.apiFetch({
                path: `/wp/v2/pages/${page.id}`,
                method: 'DELETE'
            });
            console.log(`  ✅ Deleted: ${page.title.rendered} (${page.slug})`);
        }

        console.log("\n✅ Cleanup complete!");
    } catch (err) {
        console.error("Cleanup error:", err);
    }

    console.log("\n🚀 STEP 2/2: Creating fresh pages...\n");
    console.log("Waiting 2 seconds for WordPress to update...");
    await new Promise(r => setTimeout(r, 2000));

    // Now load and run the migration script content
    alert("Cleanup done! Now copy and paste the mass_migration_full.js script to create fresh pages.");
})();
