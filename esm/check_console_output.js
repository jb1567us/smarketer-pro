// Quick check: Did the migration actually work?
(async () => {
    console.log("Checking if migration worked...\n");

    // Test with "A Day at the Lake"
    const testTitle = "A Day at the Lake";

    try {
        const pages = await wp.apiFetch({
            path: `/wp/v2/pages?search=${encodeURIComponent(testTitle)}`
        });

        console.log(`Search results for "${testTitle}":`, pages.length, "page(s) found");

        if (pages.length === 0) {
            console.error("❌ NO PAGES FOUND!");
            console.error("The migration script likely had an error.");
            console.error("\nScroll up in this console to look for RED error messages.");
            console.error("Common issues:");
            console.error("  - 'wp is not defined' = wrong tab");
            console.error("  - 'processMassBatch is not a function' = script didn't paste completely");
            console.error("  - No error but no alert = script didn't finish");
            return;
        }

        const page = pages[0];
        console.log("\n✅ Found page:");
        console.log("  Title:", page.title.rendered);
        console.log("  URL:", page.link);
        console.log("  Status:", page.status);

        // Check content
        const content = page.content.rendered;
        const hasImage = content.includes('<img');
        const imageMatch = content.match(/src="([^"]+)"/);

        console.log("\n📄 Content check:");
        console.log("  Has <img> tag:", hasImage ? "✅ YES" : "❌ NO");
        if (imageMatch) {
            console.log("  Image URL:", imageMatch[1]);
        }
        console.log("  Content length:", content.length, "characters");

        // Show snippet
        console.log("\n📋 First 500 chars of content:");
        console.log(content.substring(0, 500));

    } catch (err) {
        console.error("❌ ERROR:", err.message);
        console.error("Full error:", err);
    }
})();
