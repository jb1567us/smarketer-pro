// MIGRATION STATUS CHECKER
(async () => {
    console.log("🔍 Checking migration status for all 19 pages...\n");

    if (typeof wp === 'undefined' || !wp.apiFetch) {
        console.error("❌ WP API not available. Run this in WordPress Admin console.");
        return;
    }

    const expectedPages = [
        "A Day at the Lake",
        "A day at the park",
        "A day at the beach",
        "Gold Series 011",
        "Gold Series 010",
        "Gold Series 009",
        "Gold Series 008",
        "Gold Series 007",
        "Red Planet",
        "Portal",
        "Portal 2",
        "Abstract Landscape",
        "self portrait 1",
        "Convergence",
        "Puzzled",
        "Finger print",
        "Sheet Music",
        "Meeting in the Middle",
        "Caviar"
    ];

    const results = {
        found: 0,
        missing: 0,
        hasImage: 0,
        noImage: 0,
        wrongDomain: 0,
        details: []
    };

    for (const title of expectedPages) {
        try {
            const pages = await wp.apiFetch({
                path: `/wp/v2/pages?search=${encodeURIComponent(title)}&per_page=10`
            });

            const exactMatch = pages.find(p =>
                p.title.rendered === title ||
                p.title.rendered === title + " Painting"
            );

            if (exactMatch) {
                results.found++;
                const content = exactMatch.content.rendered;
                const imgMatch = content.match(/<img[^>]+src="([^"]+)"/);
                const hasCorrectImage = imgMatch && imgMatch[1].includes('elliotspencermorgan.com');
                const hasOldDomain = imgMatch && imgMatch[1].includes('lookoverhere.xyz');
                // Check if filename matches Underscore pattern (Server Reality)
                const isUnderscore = imgMatch && imgMatch[1].includes('_');

                if (hasCorrectImage) results.hasImage++;
                else results.noImage++;

                if (hasOldDomain) results.wrongDomain++;

                let statusIcon = '✅ OK';
                if (!hasCorrectImage) statusIcon = '❌ MISSING';
                else if (hasOldDomain) statusIcon = '❌ OLD DOMAIN';
                else if (imgMatch && !isUnderscore && !imgMatch[1].includes('GOLD')) statusIcon = '⚠️ HYPHEN?'; // Warn if hyphen used, but might work if fallback worked? No, we want underscores.

                results.details.push({
                    title: exactMatch.title.rendered,
                    status: '✅ FOUND',
                    url: exactMatch.link,
                    slug: exactMatch.slug,
                    image: statusIcon,
                    imageUrl: imgMatch ? imgMatch[1].substring(0, 60) + '...' : 'NONE'
                });
            } else {
                results.missing++;
                results.details.push({
                    title: title,
                    status: '❌ NOT FOUND',
                    url: '-',
                    slug: '-',
                    image: '-',
                    imageUrl: '-'
                });
            }
        } catch (err) {
            console.error(`Error checking "${title}":`, err.message);
        }
    }

    // Print Summary
    console.log("===============================================");
    console.log("📊 MIGRATION STATUS SUMMARY");
    console.log("===============================================");
    console.log(`Total Expected:      ${expectedPages.length}`);
    console.log(`✅ Found:            ${results.found}`);
    console.log(`❌ Missing:          ${results.missing}`);
    console.log(`🖼️  With Image:       ${results.hasImage}`);
    console.log(`⚠️  No Image:        ${results.noImage}`);
    console.log(`🚨 Wrong Domain:     ${results.wrongDomain}`);
    console.log("===============================================\n");

    // Print Details
    console.log("📋 DETAILED RESULTS:");
    console.table(results.details);

    // Recommendations
    console.log("\n💡 RECOMMENDATIONS:");
    if (results.missing > 0) {
        console.log("⚠️  Some pages are missing - the migration may not have run completely.");
        console.log("   → Check the console for errors when you ran the script.");
    }
    if (results.wrongDomain > 0) {
        console.log("🚨 Some pages still have the OLD domain (lookoverhere.xyz)!");
        console.log("   → Re-run the migration script to fix this.");
    }
    if (results.noImage > 0 && results.wrongDomain === 0) {
        console.log("⚠️  Some pages have missing images but correct domain.");
        console.log("   → Check if the image URLs are correct in artwork_data.json");
    }

    console.log("\n✅ Run complete!");
})();
