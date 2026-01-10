<?php
// regenerate_anemones_v2.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

// 1. Load Data
// Check current dir and document root
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

// 3. Load Template
$templatePath = __DIR__ . '/PREMIUM_ARTWORK_LAYOUT_VERTICAL.html';
if (!file_exists($templatePath))
    $templatePath = $_SERVER['DOCUMENT_ROOT'] . '/PREMIUM_ARTWORK_LAYOUT_VERTICAL.html';

$template = file_get_contents($templatePath);
if (!$template)
    die("Failed to load template from $templatePath");

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
    $content = str_replace($key, $val, $content);
}

// 6. Update DB
global $wpdb;
$slug = 'anemones';
$row = $wpdb->get_row("SELECT ID FROM {$wpdb->posts} WHERE post_name LIKE '%anemones%' LIMIT 1");

if ($row) {
    $wpdb->update($wpdb->posts, ['post_content' => $content], ['ID' => $row->ID]);
    echo "✅ Regenerated Anemones (ID {$row->ID}). New Length: " . strlen($content);
} else {
    echo "❌ Page not found in DB.";
}
?>