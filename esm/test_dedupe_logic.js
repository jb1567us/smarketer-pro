const artMap = new Map();

// Mock Data simulating the issue
const artRaw = [
    {
        "title": "Unique Piece",
        "slug": "unique-piece",
        "image_url": "http://example.com/unique.jpg",
        "width": "10",
        "height": "10"
    },
    {
        "title": "No Public Shrooms",
        "slug": "no-public-shrooms",
        "image_url": "http://example.com/shrooms1.jpg",
        // No dims
    },
    {
        "title": "No Public Shrooms",
        "slug": "no-public-shrooms",
        "image_url": "http://example.com/shrooms2.jpg",
        "width": "10",
        "height": "14" // Has dims, should replace the previous one
    }
];

// Logic from esm-trade-portal.php
artRaw.forEach(a => {
    if (!a.image_url) return;

    // Attach membership from collections (Mocked)
    a.membership = [];

    const hasDims = (a.width && a.height && a.width !== 'undefined' && a.height !== 'undefined');
    const existing = artMap.get(a.image_url);

    if (existing) {
        const existingHasDims = (existing.width && existing.height && existing.width !== 'undefined' && existing.height !== 'undefined');
        // If existing has no dims but new one DOES, replace it
        if (hasDims && !existingHasDims) {
            artMap.set(a.image_url, a);
        }
        // If both have dims or both don't, check if the NEW one is "better" (e.g. has more data)
        // For now, we stick to the first one unless the new one has dimensions and old one doesn't.
    } else {
        // NEW: Slug/Title Collision Check
        // Before adding by image_url, check if we already have this Title/Slug under a different Image URL
        let duplicateFound = false;
        for (const [key, val] of artMap.entries()) {
            // Check slug match
            if (a.slug && val.slug && a.slug === val.slug) {
                duplicateFound = true;
                console.log(`Duplicate found for slug: ${a.slug}`);
                // If new one has dims and old one doesn't, REPLACE the old key
                const valHasDims = (val.width && val.height && val.width !== 'undefined' && val.height !== 'undefined');
                if (hasDims && !valHasDims) {
                    console.log(`Replacing entry because new one has dimensions.`);
                    artMap.delete(key); // Remove old entry
                    artMap.set(a.image_url, a); // Add new one
                } else {
                    console.log(`Keeping existing entry.`);
                }
                break;
            }
        }

        if (!duplicateFound) {
            artMap.set(a.image_url, a);
        }
    }

    // Ensure link is present (Mocked)
    a.link = '/link/';
});

const artworks = Array.from(artMap.values());
console.log("Final Artworks Count:", artworks.length);
artworks.forEach(a => console.log(`- ${a.title} (${a.image_url})`));

if (artworks.length === 2) {
    console.log("TEST PASSED");
} else {
    console.log("TEST FAILED");
}
