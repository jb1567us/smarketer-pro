const fs = require('fs');

const rawData = JSON.parse(fs.readFileSync('C:/sandbox/esm/full_wordpress_inventory_all.json', 'utf8'));

// DEDUPLICATION STRATEGY
// 1. Maintain a map of Saatchi IDs to items.
// 2. Prefer 'page' over 'post'.
// 3. Exclude known non-artworks (Privacy Policy, etc - although script already filters some).

console.log(`Initial count: ${rawData.length}`);

const uniqueMap = new Map();
const duplicates = [];

rawData.forEach(item => {
    // Clean title for comparison
    const cleanTitle = item.title.replace(' Painting', '').replace(' Sculpture', '').replace(/&#8211;/g, '-').trim();
    // Use Saatchi URL as primary key if available, else cleanTitle
    const key = item.saatchi_url || cleanTitle.toLowerCase();

    // FIX IMAGE DOMAIN
    if (item.image_url && item.image_url.includes('lookoverhere.xyz/esm')) {
        item.image_url = item.image_url.replace('lookoverhere.xyz/esm', 'elliotspencermorgan.com');
    }

    if (!key) return; // Skip if no identifier (e.g. Privacy Policy with no saatchi link)

    if (uniqueMap.has(key)) {
        const existing = uniqueMap.get(key);
        // Preference logic: 'page' wins over 'post'
        if (item.type === 'page' && existing.type !== 'page') {
            uniqueMap.set(key, item);
        } else if (item.type === 'page' && existing.type === 'page') {
            // Duplicate pages? Log it.
            duplicates.push({ keep: existing, discard: item });
        } else {
            // Existing is page, new is post (ignore) or both are posts (ignore duplicate)
        }
    } else {
        uniqueMap.set(key, item);
    }
});

const cleanedInventory = Array.from(uniqueMap.values());
console.log(`Cleaned count: ${cleanedInventory.length}`);

// Merge into artwork_data.json
let masterData = [];
try {
    masterData = JSON.parse(fs.readFileSync('C:/sandbox/esm/artwork_data.json', 'utf8'));
} catch (e) {
    console.log("No existing master data found, starting fresh.");
}

// Update Master Data with discovered IDs and URLs
cleanedInventory.forEach(newItem => {
    const existingIndex = masterData.findIndex(m => m.saatchi_url === newItem.saatchi_url || m.title === newItem.title);

    if (existingIndex > -1) {
        // Merge
        masterData[existingIndex] = { ...masterData[existingIndex], ...newItem, id: newItem.id }; // Update ID!
    } else {
        // Add new
        masterData.push(newItem);
    }
});

fs.writeFileSync('C:/sandbox/esm/artwork_data.json', JSON.stringify(masterData, null, 2));
console.log("Updated master C:/sandbox/esm/artwork_data.json");
