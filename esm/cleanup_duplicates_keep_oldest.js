// Cleanup Duplicates - Keep OLDEST (Original)
(async function () {
    console.log("Starting duplicate cleanup (Keeping Originals)...");

    if (typeof wp === 'undefined' || !wp.data || !wp.apiFetch) {
        return console.error("wp.data not available. Run this in WordPress Admin.");
    }

    // Fetch all pages
    async function getAllPages() {
        let allPages = [];
        let page = 1;
        let complete = false;

        while (!complete) {
            try {
                const pages = await wp.apiFetch({ path: `/wp/v2/pages?per_page=100&page=${page}&status=any` });
                if (pages.length === 0) {
                    complete = true;
                } else {
                    allPages = allPages.concat(pages);
                    page++;
                    console.log(`Fetched page ${page - 1} (${pages.length} items)...`);
                }
            } catch (err) {
                console.error("Error fetching page " + page, err);
                complete = true;
            }
        }
        return allPages;
    }

    const allPages = await getAllPages();
    console.log(`Total pages found: ${allPages.length}`);

    // Group by title (case-insensitive) OR Slug Base
    const groups = {};

    function normalizeSlug(slug) {
        // remove -2, -3 suffix
        return slug.replace(/-\d+$/, '');
    }

    allPages.forEach(page => {
        // Use normalized title as key
        const key = page.title.rendered.toLowerCase().trim();
        // Alternative: group by normalized slug? 
        // Let's stick to title for now as duplicates usually share title
        if (!groups[key]) {
            groups[key] = [];
        }
        groups[key].push(page);
    });

    // Find duplicates
    const duplicates = Object.entries(groups).filter(([title, pages]) => pages.length > 1);

    console.log(`Found ${duplicates.length} duplicate groups`);

    if (duplicates.length === 0) {
        alert("No duplicates found!");
        return;
    }

    // Show duplicates and prepare for deletion
    const toDelete = [];

    console.log("Analyzing duplicates...");

    duplicates.forEach(([title, pages]) => {
        // Sort by date ASCENDING (Oldest first)
        pages.sort((a, b) => new Date(a.date) - new Date(b.date));

        // Keep the first (OLDEST - The Original), delete the rest (New Duplicates)
        const keep = pages[0];
        const remove = pages.slice(1);

        console.log(`\nGroup: "${title}"`);
        console.log(`  KEEP (Oldest): ID ${keep.id} (Slug: ${keep.slug}, Date: ${keep.date})`);

        remove.forEach(p => {
            console.log(`  DELETE (Newer): ID ${p.id} (Slug: ${p.slug}, Date: ${p.date})`);
            toDelete.push(p.id);
        });
    });

    console.log(`\n=== SUMMARY ===`);
    console.log(`Total duplicates to delete: ${toDelete.length}`);

    // Confirm before deletion
    const confirm = window.confirm(`Found ${duplicates.length} groups of duplicates.\n\nWill DELETE ${toDelete.length} newer pages and KEEP the oldest versions.\n\nProceed?`);

    if (!confirm) {
        console.log("Deletion cancelled.");
        return;
    }

    // Delete duplicates
    console.log("\nDeleting duplicates...");
    let deleted = 0;
    let errors = 0;

    // Process in batches
    for (const pageId of toDelete) {
        try {
            await wp.apiFetch({
                path: `/wp/v2/pages/${pageId}`,
                method: 'DELETE'
            });
            deleted++;
            console.log(`Deleted page ${pageId} (${deleted}/${toDelete.length})`);
        } catch (err) {
            errors++;
            console.error(`Failed to delete page ${pageId}:`, err);
        }
    }

    console.log(`\n=== COMPLETE ===`);
    console.log(`Successfully deleted: ${deleted}`);
    console.log(`Remaining pages: ${allPages.length - deleted}`);
    alert(`Cleanup Complete! Deleted ${deleted} duplicate pages.`);

})();
