<?php
// clean_all_artwork_content.php
// Iterates through all Artwork Pages and replaces content with [esm_artwork_layout]
// This ensures DB hygiene, removing old broken HTML/CSS.
// The actual rendering is handled by the V3 Plugin Filter.

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

// 1. Load Artwork Data to get target IDs
$json_file = $_SERVER['DOCUMENT_ROOT'] . '/artwork_data.json';
if (!file_exists($json_file))
    die("JSON not found");

$data = json_decode(file_get_contents($json_file), true);
$target_ids = [];

foreach ($data as $item) {
    if (isset($item['wordpress_id']) && $item['type'] === 'page') {
        $target_ids[] = $item['wordpress_id'];
    }
}

echo "<h1>Global Content Cleaner</h1>";
echo "Found " . count($target_ids) . " targets in JSON.<br><hr>";

$count_updated = 0;
$count_skipped = 0;
$target_content = '[esm_artwork_layout]';

foreach ($target_ids as $id) {
    $post = get_post($id);
    if (!$post) {
        echo "❌ ID $id not found.<br>";
        continue;
    }

    // Check if update needed
    if (trim($post->post_content) === $target_content) {
        echo "Example: " . $post->post_title . " (Clean)<br>";
        $count_skipped++;
        continue;
    }

    // Update
    $updated = wp_update_post([
        'ID' => $id,
        'post_content' => $target_content
    ]);

    if ($updated) {
        echo "✅ Cleaned: <strong>" . $post->post_title . "</strong><br>";
        $count_updated++;
    } else {
        echo "❌ Failed: " . $post->post_title . "<br>";
    }
}

echo "<hr><h2>Summary</h2>";
echo "Updated: $count_updated<br>";
echo "Already Clean: $count_skipped<br>";
?>