const fs = require('fs');
const https = require('https');
const path = require('path');

// 1. Data
const data = require('./artwork_data.json');
const outputDir = path.join(__dirname, 'images');

if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir);
}

// 2. Download Helper
const downloadImage = (url, filepath) => {
    return new Promise((resolve, reject) => {
        const file = fs.createWriteStream(filepath);
        https.get(url, response => {
            if (response.statusCode === 200) {
                response.pipe(file);
                file.on('finish', () => {
                    file.close(resolve);
                });
            } else {
                file.close();
                fs.unlink(filepath, () => { }); // Delete partial
                reject(`Server responded with ${response.statusCode}: ${url}`);
            }
        }).on('error', err => {
            fs.unlink(filepath, () => { });
            reject(err.message);
        });
    });
};

// 3. Process
(async () => {
    console.log(`Downloading ${data.length} images...`);

    for (const item of data) {
        // Skip items with known missing images or handle errors
        const filename = path.basename(item.image_url);
        const filepath = path.join(outputDir, filename);

        if (item.scrape_failed && !item.image_url.includes('upload')) {
            console.log(`Skipping broken item: ${item.title}`);
            continue;
        }

        try {
            console.log(`Downloading ${item.title}...`);
            await downloadImage(item.image_url, filepath);
            console.log(`✅ Saved ${filename}`);
        } catch (err) {
            console.error(`❌ Failed ${item.title}: ${err}`);
        }
    }
})();
