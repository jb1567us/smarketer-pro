
(function () {
    console.log("Starting batch artwork page creation...");

    // 1. Define the Master Template (Minified/Stringified version of PREMIUM_ARTWORK_LAYOUT_VERTICAL.html)
    // We will use placeholders {{TITLE}}, {{IMAGE_URL}}, {{PRICE}}, {{TAGS_DISPLAY}}, {{TAGS_DATA}}
    const layoutTemplate = `<!-- wp:html -->
<!-- Premium Artwork Page Styles -->
<style>
    /* Font Imports */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Inter:wght@300;400;500;600&display=swap');

    /* Container Reset */
    .artwork-page-container {
        font-family: 'Inter', sans-serif;
        color: #2c3e50;
        max-width: 100%;
        margin: 0 auto;
        line-height: 1.6;
    }

    /* Typography */
    .artwork-header {
        text-align: center;
        margin-bottom: 2rem;
    }

    .artwork-title {
        font-family: 'Playfair Display', serif;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        font-weight: 400;
        color: #1a1a1a;
    }

    .artwork-price {
        font-size: 1.25rem;
        color: #666;
        font-weight: 300;
    }

    /* Image Styling - Breakout */
    .artwork-hero-image {
        width: 100vw;
        max-width: 100vw;
        margin-left: 50%;
        transform: translateX(-50%);
        height: auto;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        margin-bottom: 2.5rem;

        /* Limit max width on very large screens */
        @media (min-width: 800px) {
            max-width: 800px;
        }
    }

    /* Action Buttons */
    .artwork-actions {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        margin-bottom: 2.5rem;
    }

    .btn-premium {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 1rem 1.5rem;
        border-radius: 4px;
        text-decoration: none;
        font-weight: 500;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-size: 0.9rem;
    }

    .btn-saatchi {
        background-color: #1a1a1a;
        color: #ffffff !important;
        border: 1px solid #1a1a1a;
    }

    .btn-saatchi:hover {
        background-color: #333;
        transform: translateY(-1px);
    }

    .btn-trade {
        background-color: transparent;
        color: #1a1a1a !important;
        border: 1px solid #1a1a1a;
    }

    .btn-trade:hover {
        background-color: #f8f9fa;
        color: #000 !important;
    }

    /* Details Card */
    .details-card {
        background-color: #ffffff;
        padding: 0;
        margin-bottom: 2.5rem;
        border-top: 1px solid #eee;
        border-bottom: 1px solid #eee;
    }

    .details-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0;
    }

    .detail-item {
        display: flex;
        flex-direction: column;
        padding: 1rem;
        border-right: 1px solid #eee;
        border-bottom: 1px solid #eee;
    }

    .detail-item:nth-child(2n) {
        border-right: none;
    }

    .detail-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #1a1a1a;
        margin-bottom: 0.35rem;
        font-weight: 700;
    }

    .detail-value {
        font-weight: 400;
        color: #1a1a1a;
        font-size: 1.1rem;
        font-family: 'Playfair Display', serif;
    }

    /* Content Sections */
    .artwork-description {
        font-size: 1.05rem;
        margin-bottom: 3rem;
        color: #4a4a4a;
    }

    .section-divider {
        height: 1px;
        background: #e0e0e0;
        margin: 3rem 0;
        border: none;
    }

    /* Designer Specs Box */
    .designer-specs-premium {
        border: 1px solid #e0e0e0;
        padding: 2rem;
        border-radius: 8px;
        background: #fff;
        position: relative;
        overflow: hidden;
    }

    .designer-specs-premium::before {
        content: "TRADE ONLY";
        position: absolute;
        top: 1rem;
        right: 1rem;
        font-size: 0.6rem;
        font-weight: 700;
        border: 1px solid #1a1a1a;
        padding: 0.25rem 0.5rem;
        border-radius: 2px;
    }

    .specs-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.5rem;
        margin-bottom: 1.5rem;
    }

    .specs-list {
        list-style: none;
        padding: 0;
        margin: 0;
    }

    .specs-list li {
        padding: 0.75rem 0;
        border-bottom: 1px solid #f0f0f0;
        display: flex;
        align-items: center;
    }

    .specs-list li:last-child {
        border-bottom: none;
    }

    .check-icon {
        color: #27ae60;
        margin-right: 0.75rem;
    }
</style>

<!-- VisualArtwork Schema -->
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "VisualArtwork",
  "name": "{{TITLE}}",
  "artMedium": "Mixed media on canvas",
  "artform": "Painting",
  "artworkSurface": "Canvas",
  "artist": { "@type": "Person", "@id": "https://elliotspencermorgan.com/about#artist", "name": "Elliot Spencer Morgan" },
  "height": {"@type": "Distance", "value": "48", "unitCode": "INH"},
  "width": {"@type": "Distance", "value": "48", "unitCode": "INH"},
  "depth": {"@type": "Distance", "value": "1.5", "unitCode": "INH"},
  "artEdition": "1",
  "image": "{{IMAGE_URL}}",
  "dateCreated": "2024",
  "offers": { "@type": "Offer", "availability": "https://schema.org/InStock", "price": "{{PRICE}}", "priceCurrency": "USD" }
}
</script>

<div class="artwork-page-container">

    <!-- Header -->
    <header class="artwork-header">
        <h1 class="artwork-title">{{TITLE}}</h1>
        <div class="artwork-price">\${{PRICE}}</div>
    </header>

    <!-- Main Image -->
    <img src="{{IMAGE_URL}}"
        alt="{{TITLE}} - Mixed media abstract painting" class="artwork-hero-image">

    <!-- Actions -->
    <div class="artwork-actions">
        <a href="#" class="btn-premium btn-saatchi" onclick="gtag('event', 'saatchi_click', {'artwork': '{{TITLE}}'});">
            Purchase on Saatchi Art
        </a>
        <a href="/trade" class="btn-premium btn-trade" onclick="gtag('event', 'trade_click', {'artwork': '{{TITLE}}'});">
            Request Trade Pricing
        </a>
    </div>

    <!-- Details Card -->
    <div class="details-card">
        <div class="details-grid">
            <div class="detail-item">
                <span class="detail-label">Medium</span>
                <span class="detail-value">Mixed Media</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Dimensions</span>
                <span class="detail-value">48" × 48"</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Year</span>
                <span class="detail-value">2024</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Authenticity</span>
                <span class="detail-value">Signed Original</span>
            </div>
        </div>
    </div>

    <!-- Description -->
    <div class="artwork-description">
        <h3>About the Work</h3>
        <p>A striking contemporary abstract piece featuring intricate compositions in {{COLOR_DESC}}. The layered technique creates depth and visual rhythm.</p>
        <p><em>Dimensions available upon request. Custom framing options available for trade partners.</em></p>
    </div>

    <hr class="section-divider">

    <!-- Designer Specs (Premium Box) -->
    <div class="designer-specs-premium" {{TAGS_DATA}}>

        <h3 class="specs-title">Designer Specifications</h3>

        <ul class="specs-list">
            <li><span class="check-icon">✓</span> <strong>Installation:</strong> Wired & Ready to Hang</li>
            <li><span class="check-icon">✓</span> <strong>Weight:</strong> 5 lbs (Lightweight)</li>
            <li><span class="check-icon">✓</span> <strong>Framing:</strong> {{FRAMING}}</li>
            <li><span class="check-icon">✓</span> <strong>Lead Time:</strong> Ships in 5-7 Days</li>
            <!-- Visible Tags for Reference -->
            <li style="border-bottom: none; padding-top: 1rem; margin-top: 0.5rem; border-top: 1px dashed #eee;">
                <span style="font-size: 0.75rem; color: #999; text-transform: uppercase; letter-spacing: 1px; margin-right: 0.5rem;">Tags:</span>
                <span style="font-size: 0.85rem; color: #666;">{{TAGS_DISPLAY}}</span>
            </li>
        </ul>

        <div style="margin-top: 1.5rem; display: flex; gap: 1rem;">
             <a href="#" style="font-size: 0.9rem; color: #666; text-decoration: none; border-bottom: 1px dotted #999;">Download Spec Sheet</a>
        </div>
    </div>

    <hr class="section-divider">

    <!-- Artist Short Bio -->
    <div style="display: flex; align-items: center; gap: 1rem; margin-top: 2rem;">
        <div style="width: 60px; height: 60px; background: #eee; border-radius: 50%;"></div>
        <div>
            <h4 style="margin: 0; font-family: 'Playfair Display', serif;">Elliot Spencer Morgan</h4>
            <p style="margin: 0; font-size: 0.9rem; color: #666;">Austin, TX</p>
        </div>
        <a href="/about" style="margin-left: auto; text-decoration: none; font-size: 0.9rem; font-weight: 600;">View Profile →</a>
    </div>

</div>
<!-- /wp:html -->`;

    // 2. Define the Target Artworks Map
    const targetArtworks = [
        // RETRY: Portal - using specific slug to avoid redirect conflicts
        {
            id: 207, originalTitle: "Portal Painting", newTitle: "Portal", price: "3,000", colorDesc: "vibrant colors and depth", framing: "Gallery Wrapped",
            slug: "portal-abstract", // Force new slug
            tagsDisplay: "Vibrant, Geometric, Portal, Multi-color",
            tagsData: 'data-color-palette="multi" data-style="geometric" data-collection="statement-pieces"'
        },

        {
            id: 227, originalTitle: "Blue Glacier Painting", newTitle: "Blue Glacier", price: "2,800", colorDesc: "icy blues and white", framing: "Gallery Wrapped",
            tagsDisplay: "Blue, White, Cool, Minimal",
            tagsData: 'data-color-palette="blue-light" data-style="minimal-abstract" data-collection="water-series"'
        },

        {
            id: 206, originalTitle: "Golden Rule Painting", newTitle: "Golden Rule", price: "3,200", colorDesc: "gold and structural elements", framing: "Whitewashed Wood",
            tagsDisplay: "Gold, Structure, Warm, Large",
            tagsData: 'data-color-palette="gold" data-style="structural" data-collection="gold-series"'
        },

        {
            id: 204, originalTitle: "Transformation Painting", newTitle: "Transformation", price: "2,900", colorDesc: "shifting forms and light", framing: "Gallery Wrapped",
            tagsDisplay: "Dynamic, Shift, Multi-color, Abstract",
            tagsData: 'data-color-palette="multi" data-style="abstract-dynamic" data-collection="statement-pieces"'
        },

        {
            id: 200, originalTitle: "Bloom Painting", newTitle: "Bloom", price: "2,500", colorDesc: "organic bursting patterns", framing: "Natural Wood",
            tagsDisplay: "Organic, Floral-Abstract, Pink, Red",
            tagsData: 'data-color-palette="warm" data-style="organic" data-collection="organic-series"'
        },
    ];

    async function processBatch() {
        if (typeof wp === 'undefined' || !wp.data) {
            console.error("wp.data not available");
            return "Error: wp.data missing";
        }

        const stats = { created: 0, skipped: 0, errors: 0 };
        const results = [];

        console.log(`Processing ${targetArtworks.length} artworks...`);

        for (const artwork of targetArtworks) {
            try {
                // A. Fetch original post to get image
                // Use REST API via wp.apiFetch if available, or just fetch directly
                // wp.data.select('core').getEntityRecord('postType', 'post', id) might be cached or require resolution
                // A safer bet is just to construct the image URL if possible, BUT we don't know the image URL without fetching content.
                // However, we can use wp.apiFetch which returns a promise.

                // Let's assume we can use wp.apiFetch
                const post = await wp.apiFetch({ path: `/wp/v2/posts/${artwork.id}` });

                if (!post) {
                    console.error(`Post ${artwork.id} not found`);
                    stats.errors++;
                    results.push(`Error: Post ${artwork.id} not found`);
                    continue;
                }

                // Extract image URL from content or featured media
                let imageUrl = "";
                if (post.featured_media > 0) {
                    const media = await wp.apiFetch({ path: `/wp/v2/media/${post.featured_media}` });
                    imageUrl = media.source_url;
                } else {
                    // Try to regex it from content
                    const match = post.content.rendered.match(/src="([^"]+)"/);
                    if (match) imageUrl = match[1];
                }

                if (!imageUrl) {
                    console.warn(`No image found for ${artwork.newTitle}`);
                    // Fallback placeholder or skip? Let's use a generic placeholder for now to not break flow, or skip.
                    // Skipping is safer.
                    console.log("Skipping due to missing image");
                    stats.errors++;
                    results.push(`Skipped: No image for ${artwork.newTitle}`);
                    continue;
                }

                console.log(`Found image for ${artwork.newTitle}: ${imageUrl}`);

                // B. Prepare Content
                let content = layoutTemplate
                    .replace(/{{TITLE}}/g, artwork.newTitle)
                    .replace(/{{IMAGE_URL}}/g, imageUrl)
                    .replace(/{{PRICE}}/g, artwork.price)
                    .replace(/{{COLOR_DESC}}/g, artwork.colorDesc)
                    .replace(/{{FRAMING}}/g, artwork.framing)
                    .replace(/{{TAGS_DISPLAY}}/g, artwork.tagsDisplay)
                    .replace(/{{TAGS_DATA}}/g, artwork.tagsData);

                // C. Create New Page
                // Check if page already exists? 
                const existingPages = await wp.apiFetch({ path: `/wp/v2/pages?search=${encodeURIComponent(artwork.newTitle)}` });
                let pageIdToUpdate = null;
                if (existingPages && existingPages.length > 0) {
                    // Check exact match
                    const match = existingPages.find(p => p.title.rendered === artwork.newTitle);
                    if (match) {
                        pageIdToUpdate = match.id;
                    }
                }

                if (pageIdToUpdate) {
                    console.log(`Page '${artwork.newTitle}' already exists (ID: ${pageIdToUpdate}). Updating...`);
                    const updateData = {
                        content: content,
                        status: 'publish'
                    };
                    if (artwork.slug) updateData.slug = artwork.slug;

                    await wp.apiFetch({
                        path: `/wp/v2/pages/${pageIdToUpdate}`,
                        method: 'PUT', // Changed from POST to PUT for update
                        data: updateData
                    });
                    stats.created++; // Assuming 'created' here means 'processed' or 'updated'
                    results.push(`Updated: ${artwork.newTitle}`);
                } else {
                    const createData = {
                        title: artwork.newTitle,
                        content: content,
                        status: 'publish'
                    };
                    if (artwork.slug) createData.slug = artwork.slug;

                    const newPage = await wp.apiFetch({
                        path: '/wp/v2/pages',
                        method: 'POST',
                        data: createData
                    });

                    console.log(`Created page: ${newPage.link}`);
                    stats.created++;
                    results.push(`Created: ${artwork.newTitle} (${newPage.link})`);
                }

            } catch (err) {
                console.error(`Error processing ${artwork.newTitle}:`, err);
                stats.errors++;
                results.push(`Error ${artwork.newTitle}: ${err.message}`);
            }
        }

        return stats;
    }

    // Execute
    return processBatch().then(stats => JSON.stringify(stats));
})();
