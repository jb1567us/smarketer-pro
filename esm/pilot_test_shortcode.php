<?php
// pilot_test_shortcode.php
// Updates 'Animal Kingdom' to use the new Master Template Shortcode
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$page = get_page_by_path('animal-kingdom', OBJECT, 'page');
if ($page) {
    echo "Found 'Animal Kingdom' (ID: {$page->ID}). Updating content...<br>";

    // The Shortcode
    $new_content = '[esm_artwork_layout]';

    // Update
    wp_update_post([
        'ID' => $page->ID,
        'post_content' => $new_content
    ]);

    echo "<h1>✅ Update Complete</h1>";
    echo "Page content replaced with: <code>" . htmlspecialchars($new_content) . "</code><br>";
    echo "<a href='" . get_permalink($page->ID) . "' target='_blank'>View Page</a>";
} else {
    echo "❌ Page 'animal-kingdom' not found.";
}
?>