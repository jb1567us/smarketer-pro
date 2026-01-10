
// Run this on https://www.saatchiart.com/account/artworks/1295487 OR the public profile page.
(function () {
    console.log("Harvesting Artwork URLs...");

    // Select all links that look like artwork view pages
    // Pattern: /art/Type-Title/Id/Id/view
    const links = Array.from(document.querySelectorAll('a[href*="/art/"]'))
        .filter(a => a.href.includes('/view'))
        .map(a => a.href)
        // clean up query params if any
        .map(url => url.split('?')[0]);

    // Deduplicate
    const uniqueLinks = [...new Set(links)];

    console.log(`Found ${uniqueLinks.length} unique artwork URLs.`);
    console.log("Here is the JSON list (Copy all text below):");
    console.log(JSON.stringify(uniqueLinks, null, 2));

    // Optional: Auto-download
    const blob = new Blob([JSON.stringify(uniqueLinks, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'saatchi_master_url_list.json';
    a.click();
})();
