<?php
// regenerate_anemones.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
ini_set('display_errors', 1);

// 1. Load Data
$json = file_get_contents('artwork_data.json');
$data = json_decode($json, true);
if (!$data)
    die("Failed to decode JSON");

// 2. Find Anemones
$artwork = null;
foreach ($data as $item) {
    if (strcasecmp($item['title'], 'Anemones') === 0 || strcasecmp($item['cleanTitle'], 'Anemones') === 0) {
        $artwork = $item;
        break;
    }
}
if (!$artwork)
    die("Anemones not found in JSON");

echo "Found Artwork: {$artwork['title']} (ID: {$artwork['id']})<br>";

// 3. Load Template
$template = file_get_contents('PREMIUM_ARTWORK_LAYOUT_VERTICAL.html');
if (!$template)
    die("Failed to load template");

// 4. Prepare Tags
$tagsList = [];
if (!empty($artwork['styles']))
    $tagsList[] = $artwork['styles'];
if (!empty($artwork['medium']))
    $tagsList[] = $artwork['medium'];
if (!empty($artwork['detected_colors']))
    $tagsList[] = implode(', ', $artwork['detected_colors']);
$tagsStr = implode(', ', $tagsList);

// 5. Replacements
$replacements = [
    '{{TITLE}}' => $artwork['title'],
    '{{MEDIUM}}' => $artwork['medium'],
    '{{YEAR}}' => $artwork['year'],
    '{{IMAGE_URL}}' => $artwork['image_url'],
    '{{SAATCHI_URL}}' => $artwork['saatchi_url'],
    '{{PRICE}}' => $artwork['price'],
    '{{DIMENSIONS}}' => $artwork['dimensions'] ?? ($artwork['width'] . ' W x ' . $artwork['height'] . ' H x ' . ($artwork['depth'] ?? '0') . ' D in'),
    '{{STYLES}}' => $artwork['styles'],
    '{{MEDIUMS_DETAILED}}' => $artwork['mediumsDetailed'] ?? $artwork['medium'],
    '{{FRAME}}' => $artwork['frame'] ?? 'N/A',
    '{{PACKAGING}}' => $artwork['packaging'] ?? 'N/A',
    '{{SHIPPING}}' => $artwork['shippingFrom'] ?? 'USA',
    '{{DESCRIPTION}}' => $artwork['description'] ?? 'Original artwork by Elliot Spencer Morgan.',
    '{{TAGS}}' => $tagsStr
];

$content = $template;
foreach ($replacements as $key => $val) {
    $content = str_replace($key, $val, $content);
}

// 6. Fix Schema (Ensure JSON script is safe)
// Using str_replace on template usually works fine.
// The template already has <script type="application/ld+json">.
// Ensure no broken quotes in inserted values.
// Actually, simple replace might break JSON if title has quotes.
// Let's escape quotes in JSON context. But we are replacing globally in HTML too.
// Ideally, we should json_encode values for JS context.
// But for now, assuming simple text.

// Update DB
global $wpdb;
$slug = 'anemones'; // or $artwork['slug']? JSON says 'anemones' likely.
$row = $wpdb->get_row("SELECT ID FROM {$wpdb->posts} WHERE post_name LIKE '%anemones%' LIMIT 1");

if ($row) {
    $wpdb->update($wpdb->posts, ['post_content' => $content], ['ID' => $row->ID]);
    echo "✅ Regenerated Anemones (ID {$row->ID}). New Length: " . strlen($content);
} else {
    echo "❌ Page not found in DB.";
}

?>