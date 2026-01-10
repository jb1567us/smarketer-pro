<?php
// regenerate_anemones_embedded.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

// 1. Load Data (Still need this, or I can hardcode Anemones data for this specific test too? No, let's try reading json, it should work)
$jsonPath = __DIR__ . '/artwork_data.json';
if (!file_exists($jsonPath))
    $jsonPath = $_SERVER['DOCUMENT_ROOT'] . '/artwork_data.json';
$json = file_get_contents($jsonPath);
$data = json_decode($json, true);
if (!$data)
    die("Failed to decode JSON from $jsonPath");

// 2. Find Anemones
$artwork = null;
foreach ($data as $item) {
    $t = $item['title'] ?? '';
    $ct = $item['cleanTitle'] ?? '';
    if (strcasecmp($t, 'Anemones') === 0 || strcasecmp($ct, 'Anemones') === 0) {
        $artwork = $item;
        break;
    }
}
if (!$artwork)
    die("Anemones not found in JSON");

echo "Found Artwork: {$artwork['title']} (ID: {$artwork['id']})<br>";

// 3. Embedded Template
$template = <<<HTML
<!-- wp:html -->
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
        /* Large size */
        margin-bottom: 0.5rem;
        font-weight: 400;
        color: #1a1a1a;
    }

    .artwork-price {
        font-size: 1.75rem;
        color: #1a1a1a;
        font-weight: 400;
        margin-top: 0.5rem;
        font-family: 'Playfair Display', serif;
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

        /* Limit max width on very large screens to avoid being too huge */
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

    /* Details Card - Refined */
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
        /* Removing gap for bordered look */
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
        /* No border on right column */
    }

    .detail-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        color: #1a1a1a;
        /* Darker color */
        margin-bottom: 0.35rem;
        font-weight: 700;
        /* Bold */
    }

    .detail-value {
        font-weight: 400;
        color: #1a1a1a;
        font-size: 1.1rem;
        font-family: 'Playfair Display', serif;
        /* Serif for values to contrast with sans-serif label */
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

    /* Designer Specs Box (Refined) */
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
  "artMedium": "{{MEDIUM}}",
  "artform": "Painting",
  "artworkSurface": "Canvas",
  "artist": { "@type": "Person", "@id": "https://elliotspencermorgan.com/about#artist", "name": "Elliot Spencer Morgan" },
  "height": {"@type": "Distance", "value": "48", "unitCode": "INH"},
  "width": {"@type": "Distance", "value": "48", "unitCode": "INH"},
  "depth": {"@type": "Distance", "value": "1.5", "unitCode": "INH"},
  "artEdition": "1",
  "image": "{{IMAGE_URL}}",
  "dateCreated": "{{YEAR}}",
  "sameAs": "{{SAATCHI_URL}}",
  "offers": { "@type": "Offer", "availability": "https://schema.org/InStock", "url": "{{SAATCHI_URL}}", "price": "{{PRICE}}", "priceCurrency": "USD" }
}
</script>

<div class="artwork-page-container">

    <!-- Header -->
    <header class="artwork-header">
        <h1 class="artwork-title">{{TITLE}}</h1>
        <div class="artwork-price">\${{PRICE}}</div>
    </header>

    <!-- Main Image -->
    <img src="{{IMAGE_URL}}" alt="{{TITLE}} - Abstract Art by Elliot Spencer Morgan" class="artwork-hero-image">

    <!-- Actions -->
    <div class="artwork-actions">
        <a href="{{SAATCHI_URL}}" class="btn-premium btn-saatchi"
            onclick="gtag('event', 'saatchi_click', {'artwork': '{{TITLE}}'});">
            Purchase on Saatchi Art
        </a>
        <a href="/trade" class="btn-premium btn-trade" onclick="gtag('event', 'trade_click', {'artwork': 'Caviar'});">
            Request Trade Pricing
        </a>
    </div>

    <!-- Details Section -->
    <div style="margin-top: 3rem; padding-top: 2rem; border-top: 1px solid rgba(0,0,0,0.1);">
        <h3 style="font-family: 'Playfair Display', serif; font-size: 1.5rem; margin-bottom: 1.5rem;">Details &
            Dimensions</h3>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; font-size: 0.95rem; color: #555;">
            <div><strong>Dimensions:</strong></div>
            <div>{{DIMENSIONS}}</div>

            <div><strong>Styles:</strong></div>
            <div>{{STYLES}}</div>

            <div><strong>Mediums:</strong></div>
            <div>{{MEDIUMS_DETAILED}}</div>

            <div><strong>Frame:</strong></div>
            <div>{{FRAME}}</div>

            <div><strong>Packaging:</strong></div>
            <div>{{PACKAGING}}</div>

            <div><strong>Shipping:</strong></div>
            <div>{{SHIPPING}}</div>
        </div>
    </div>

    <!-- Description -->
    <div class="artwork-description">
        <h3>About the Work</h3>
        <p>{{DESCRIPTION}}</p>
    </div>

    <hr class="section-divider">

    <!-- Designer Specs (Premium Box) -->
    <div class="designer-specs-premium" data-size-category="oversized" data-color-palette="blue-indigo"
        data-style="abstract-geometric" data-collection="2024-collection">

        <h3 class="specs-title">Designer Specifications</h3>

        <ul class="specs-list">
            <li><span class="check-icon">✓</span> <strong>Installation:</strong> Wired & Ready to Hang</li>
            <li><span class="check-icon">✓</span> <strong>Weight:</strong> 5 lbs (Lightweight)</li>
            <li><span class="check-icon">✓</span> <strong>Framing:</strong> Gallery Wrapped (Unframed)</li>
            <li><span class="check-icon">✓</span> <strong>Lead Time:</strong> Ships in 5-7 Days</li>
            <!-- Visible Tags for Reference -->
            <li style="border-bottom: none; padding-top: 1rem; margin-top: 0.5rem; border-top: 1px dashed #eee;">
                <span
                    style="font-size: 0.75rem; color: #999; text-transform: uppercase; letter-spacing: 1px; margin-right: 0.5rem;">Tags:</span>
                <span style="font-size: 0.85rem; color: #666;">{{TAGS}}</span>
            </li>
        </ul>

        <div style="margin-top: 1.5rem; display: flex; gap: 1rem;">
            <a href="/downloads/caviar-spec-sheet.pdf"
                style="font-size: 0.9rem; color: #666; text-decoration: none; border-bottom: 1px dotted #999;">Download
                Spec Sheet</a>
            <a href="/downloads/caviar-high-res.zip"
                style="font-size: 0.9rem; color: #666; text-decoration: none; border-bottom: 1px dotted #999;">High-Res
                Images</a>
        </div>
    </div>

    <hr class="section-divider">

    <!-- Artist Short Bio -->
    <div style="display: flex; align-items: center; gap: 1rem; margin-top: 2rem;">
        <div style="width: 60px; height: 60px; background: #eee; border-radius: 50%;"></div>
        <!-- Placeholder for Artist Photo -->
        <div>
            <h4 style="margin: 0; font-family: 'Playfair Display', serif;">Elliot Spencer Morgan</h4>
            <p style="margin: 0; font-size: 0.9rem; color: #666;">Austin, TX</p>
        </div>
        <a href="/about" style="margin-left: auto; text-decoration: none; font-size: 0.9rem; font-weight: 600;">View
            Profile →</a>
    </div>

</div>
<!-- /wp:html -->
HTML;

// 4. Prepare Tags
$tagsList = [];
if (!empty($artwork['styles']))
    $tagsList[] = $artwork['styles'];
if (!empty($artwork['medium']))
    $tagsList[] = $artwork['medium'];
if (!empty($artwork['detected_colors'])) {
    $colors = is_array($artwork['detected_colors']) ? $artwork['detected_colors'] : [$artwork['detected_colors']];
    $tagsList[] = implode(', ', $colors);
}
$tagsStr = implode(', ', $tagsList);

// 5. Replacements
$replacements = [
    '{{TITLE}}' => $artwork['title'] ?? 'Anemones',
    '{{MEDIUM}}' => $artwork['medium'] ?? 'Oil on Canvas',
    '{{YEAR}}' => $artwork['year'] ?? date('Y'),
    '{{IMAGE_URL}}' => $artwork['image_url'] ?? '',
    '{{SAATCHI_URL}}' => $artwork['saatchi_url'] ?? '#',
    '{{PRICE}}' => $artwork['price'] ?? '0',
    '{{DIMENSIONS}}' => $artwork['dimensions'] ?? (($artwork['width'] ?? '0') . ' W x ' . ($artwork['height'] ?? '0') . ' H'),
    '{{STYLES}}' => $artwork['styles'] ?? '',
    '{{MEDIUMS_DETAILED}}' => $artwork['mediumsDetailed'] ?? ($artwork['medium'] ?? ''),
    '{{FRAME}}' => $artwork['frame'] ?? 'N/A',
    '{{PACKAGING}}' => $artwork['packaging'] ?? 'N/A',
    '{{SHIPPING}}' => $artwork['shippingFrom'] ?? 'USA',
    '{{DESCRIPTION}}' => $artwork['description'] ?? 'Original artwork by Elliot Spencer Morgan.',
    '{{TAGS}}' => $tagsStr
];

$content = $template;
foreach ($replacements as $key => $val) {
    // Basic replacement
    $content = str_replace($key, $val, $content);
}

// 6. Update DB
global $wpdb;
$slug = 'anemones';
$row = $wpdb->get_row("SELECT ID FROM {$wpdb->posts} WHERE post_name LIKE '%anemones%' LIMIT 1");

if ($row) {
    $wpdb->update($wpdb->posts, ['post_content' => $content], ['ID' => $row->ID]);
    echo "✅ Regenerated Anemones (ID {$row->ID}). New Length: " . strlen($content);
    if (function_exists('w3tc_flush_all'))
        w3tc_flush_all();
    if (function_exists('wp_cache_flush'))
        wp_cache_flush();
} else {
    echo "❌ Page not found in DB.";
}
?>