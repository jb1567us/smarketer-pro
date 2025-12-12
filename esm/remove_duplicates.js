// Remove Duplicate Pages - Keep Most Recent
(async function () {
    console.log("Starting duplicate cleanup...");

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
                const pages = await wp.apiFetch({ path: `/wp/v2/pages?per_page=100&page=${page}` });
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

    // Group by title (case-insensitive)
    const groups = {};
    allPages.forEach(page => {
        const key = page.title.rendered.toLowerCase().trim();
        if (!groups[key]) {
            groups[key] = [];
        }
        groups[key].push(page);
    });

    // Find duplicates
    const duplicates = Object.entries(groups).filter(([title, pages]) => pages.length > 1);

    console.log(`Found ${duplicates.length} duplicate groups`);

    if (duplicates.length === 0) {
        console.log("No duplicates found!");
        return;
    }

    // Show duplicates and prepare for deletion
    const toDelete = [];
    duplicates.forEach(([title, pages]) => {
        console.log(`\nDuplicate: "${title}" (${pages.length} copies)`);

        // Sort by date (newest first)
        pages.sort((a, b) => new Date(b.date) - new Date(a.date));

        // Keep the first (newest), delete the rest
        const keep = pages[0];
        const remove = pages.slice(1);

        console.log(`  KEEP: ID ${keep.id} (${keep.date})`);
        remove.forEach(p => {
            console.log(`  DELETE: ID ${p.id} (${p.date})`);
            toDelete.push(p.id);
        });
    });

    console.log(`\n=== SUMMARY ===`);
    console.log(`Total duplicates to delete: ${toDelete.length}`);

    // Confirm before deletion
    const confirm = window.confirm(`Delete ${toDelete.length} duplicate pages? (Keeping the most recent version of each)`);

    if (!confirm) {
        console.log("Deletion cancelled.");
        return;
    }

    // Delete duplicates
    console.log("\nDeleting duplicates...");
    let deleted = 0;
    let errors = 0;

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
    console.log(`Errors: ${errors}`);
    console.log(`Remaining pages: ${allPages.length - deleted}`);
})();
