<?php
// find_image_id.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$search = "Dark";
echo "<h1>Searching for '$search' in Media Library</h1>";

// Check content of the page itself
$page_id = 2256;
$page = get_post($page_id);
if ($page) {
    echo "<h2>Content of Page $page_id ({$page->post_title})</h2>";
    echo "<pre>" . htmlspecialchars($page->post_content) . "</pre>";
}

global $wpdb;
$query = "SELECT ID, post_title, guid FROM $wpdb->posts WHERE post_type = 'attachment' AND (post_title LIKE %s OR guid LIKE %s) LIMIT 20";
$like = '%' . $wpdb->esc_like($search) . '%';

$results = $wpdb->get_results($wpdb->prepare($query, $like, $like));

if ($results) {
    echo "<ul>";
    foreach ($results as $row) {
        echo "<li>ID: $row->ID | Title: $row->post_title | GUID: $row->guid</li>";
    }
    echo "</ul>";
} else {
    echo "No matches found.";
}
?>
