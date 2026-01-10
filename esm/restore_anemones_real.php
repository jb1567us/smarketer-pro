<?php
// restore_anemones_real.php
// Regenerate Anemones content from JSON + Template

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

// 1. Load Data
$json = file_get_contents('artwork_data.json');
$data = json_decode($json, true);
$anemones = null;

// Find Anemones by slug or crude check
foreach ($data as $item) {
    if (strpos(strtolower($item['title']), 'anemones') !== false) {
        $anemones = $item;
        break;
    }
}

if (!$anemones)
    die("❌ Anemones data not found in JSON.");

// 2. Load Template
$template = file_get_contents('PREMIUM_ARTWORK_LAYOUT_VERTICAL.html');
if (!$template)
    die("❌ HTML Template not found.");

// 3. Replacements
$replacements = [
    '{{TITLE}}' => $anemones['title'],
    '{{IMAGE_URL}}' => $anemones['image_url'], // Ensure this is the correct keys
    '{{WIDTH}}' => $anemones['width_in'],
    '{{HEIGHT}}' => $anemones['height_in'],
    '{{MEDIUM}}' => $anemones['medium'] ?? 'Mixed Media',
    '{{YEAR}}' => $anemones['year'] ?? date('Y'),
    '{{PRICE}}' => $anemones['price'] ?? '$2,400',
    '{{STATUS}}' => $anemones['status'] ?? 'Available',
    '{{DESCRIPTION}}' => $anemones['description'] ?? 'A vibrant exploration of organic forms.',
    '{{SLUG}}' => 'anemones'
];

// Simple mustache-style replace
$content = $template;
foreach ($replacements as $key => $val) {
    $content = str_replace($key, $val, $content);
}

// 4. Update DB
$post_id = 213; // Anemones ID
$update = [
    'ID' => $post_id,
    'post_content' => $content
];

$res = wp_update_post($update);

if ($res) {
    echo "<h1>✅ Restored Anemones Content</h1>";
    echo "Generated " . strlen($content) . " bytes.<br>";
    echo "View: <a href='/anemones/'>/anemones/</a>";
} else {
    echo "❌ Update failed.";
}
?>