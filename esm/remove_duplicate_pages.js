// Remove Duplicate WordPress Pages (Keep cleanest slug)
(async function () {
    console.log("Finding duplicate artwork pages...");

    if (typeof wp === 'undefined' || !wp.data || !wp.apiFetch) {
        return console.error("wp.data not available. Run in WordPress Admin.");
    }

    // Fetch all pages
    let allPages = [];
    let page = 1;
    let complete = false;

    while (!complete) {
        try {
            const pages = await wp.apiFetch({
                path: `/wp/v2/pages?per_page=100&page=${page}`
            });

            if (pages.length === 0) {
                complete = true;
            } else {
                allPages = allPages.concat(pages);
                page++;
            }
        } catch (err) {
            console.error("Error fetching page " + page, err);
            complete = true;
        }
    }

    console.log(`Total pages: ${allPages.length}`);

    // Normalize title for grouping
    function normalizeTitle(title) {
        return title.toLowerCase()
            .replace(/&[#\w]+;/g, '') // Remove HTML entities
            .replace(/painting|sculpture|collage/gi, '')
            .trim();
    }

    // Group by normalized title
    const groups = {};
    allPages.forEach(p => {
        const key = normalizeTitle(p.title.rendered);
        if (!groups[key]) {
            groups[key] = [];
        }
        groups[key].push(p);
    });

    // Find duplicates
    const duplicateGroups = Object.entries(groups).filter(([title, pages]) => pages.length > 1);

    console.log(`\nFound ${duplicateGroups.length} duplicate groups`);

    if (duplicateGroups.length === 0) {
        console.log("No duplicates found!");
        return;
    }

    // For each group, keep the cleanest slug
    const toDelete = [];

    duplicateGroups.forEach(([title, pages]) => {
        console.log(`\nDuplicate: "${title}" (${pages.length} copies)`);

        // Sort by slug quality: no suffix > -2, -3, etc
        pages.sort((a, b) => {
            const aSuffix = a.slug.match(/-(\d+)$/);
            const bSuffix = b.slug.match(/-(\d+)$/);

            // No suffix beats suffix
            if (!aSuffix && bSuffix) return -1;
            if (aSuffix && !bSuffix) return 1;

            // Both have suffix, prefer lower number
            if (aSuffix && bSuffix) {
                return parseInt(aSuffix[1]) - parseInt(bSuffix[1]);
            }

            // Both no suffix, prefer newer
            return new Date(b.date) - new Date(a.date);
        });

        const keep = pages[0];
        const remove = pages.slice(1);

        console.log(`  KEEP: "${keep.title.rendered}" (slug: ${keep.slug})`);
        remove.forEach(p => {
            console.log(`  DELETE: "${p.title.rendered}" (slug: ${p.slug})`);
            toDelete.push(p);
        });
    });

    console.log(`\n=== SUMMARY ===`);
    console.log(`Duplicates to delete: ${toDelete.length}`);

    if (toDelete.length === 0) {
        console.log("Nothing to delete!");
        return;
    }

    // Confirm
    const confirm = window.confirm(`Delete ${toDelete.length} duplicate pages? (Keeping the cleanest slug of each)`);

    if (!confirm) {
        console.log("Cancelled.");
        return;
    }

    // Delete
    console.log("\nDeleting duplicates...");
    let deleted = 0;
    let errors = 0;

    for (const p of toDelete) {
        try {
            await wp.apiFetch({
                path: `/wp/v2/pages/${p.id}`,
                method: 'DELETE'
            });
            deleted++;
            console.log(`✅ Deleted: ${p.title.rendered} (${deleted}/${toDelete.length})`);
        } catch (err) {
            errors++;
            console.error(`❌ Failed: ${p.title.rendered}`, err);
        }
    }

    console.log(`\n=== COMPLETE ===`);
    console.log(`Deleted: ${deleted}`);
    console.log(`Errors: ${errors}`);
    console.log(`Remaining pages: ${allPages.length - deleted}`);
})();
