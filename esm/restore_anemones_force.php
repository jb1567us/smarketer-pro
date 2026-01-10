<?php
// restore_anemones_force.php
// DIRECT SQL UPDATE to bypass WP Filters/Revisions

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
global $wpdb;

// 1. Load Data
$json = file_get_contents('artwork_data.json');
$data = json_decode($json, true);
$anemones = null;
foreach ($data as $item) {
    if (strpos(strtolower($item['title']), 'anemones') !== false) {
        $anemones = $item;
        break;
    }
}
if (!$anemones)
    die("❌ Data missing.");

// 2. Load Template
$template = file_get_contents('PREMIUM_ARTWORK_LAYOUT_VERTICAL.html');
if (!$template)
    die("❌ Template missing.");

// 3. Replacements
$replacements = [
    '{{TITLE}}' => $anemones['title'],
    '{{IMAGE_URL}}' => $anemones['image_url'],
    '{{WIDTH}}' => $anemones['width_in'],
    '{{HEIGHT}}' => $anemones['height_in'],
    '{{MEDIUM}}' => $anemones['medium'] ?? 'Mixed Media',
    '{{YEAR}}' => $anemones['year'] ?? date('Y'),
    '{{PRICE}}' => $anemones['price'] ?? '$2,400',
    '{{STATUS}}' => $anemones['status'] ?? 'Available',
    '{{DESCRIPTION}}' => $anemones['description'] ?? 'A vibrant exploration of organic forms.',
    '{{SLUG}}' => 'anemones'
];
$content = $template;
foreach ($replacements as $key => $val) {
    $content = str_replace($key, $val, $content);
}

// 4. FORCE UPDATE via SQL
$post_id = 213;
$wpdb->query(
    $wpdb->prepare(
        "UPDATE $wpdb->posts SET post_content = %s WHERE ID = %d",
        $content,
        $post_id
    )
);

echo "<h1>✅ FORCED SQL UPDATE</h1>";
echo "Updated Post $post_id directly.<br>";

// Verify
$check = $wpdb->get_var("SELECT post_content FROM $wpdb->posts WHERE ID = $post_id");
echo "Current DB Length: " . strlen($check) . " chars.<br>";
if (strpos($check, 'artwork-page-container') !== false) {
    echo "✅ Content Verified in DB.";
} else {
    echo "❌ Content Verification Failed.";
}
?>