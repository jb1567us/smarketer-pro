<?php
// find_image_id_v2.php
header("Cache-Control: no-store, no-cache, must-revalidate, max-age=0");
header("Cache-Control: post-check=0, pre-check=0", false);
header("Pragma: no-cache");

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$search = "In_the_DarkPainting";
echo "<h1>Searching for '$search' in Media Library</h1>";

// Comment out page content dump
/*
$page_id = 2256;
$page = get_post($page_id);
if ($page) {
    echo "<h2>Content of Page $page_id ({$page->post_title})</h2>";
    echo "<pre>" . htmlspecialchars($page->post_content) . "</pre>";
}
*/

global $wpdb;
$query = "SELECT ID, post_title, guid FROM $wpdb->posts WHERE post_type = 'attachment' AND guid LIKE %s LIMIT 50";
$like = '%' . $wpdb->esc_like($search) . '%';

$results = $wpdb->get_results($wpdb->prepare($query, $like));

if ($results) {
    echo "<ul>";
    foreach ($results as $row) {
        $img = wp_get_attachment_image_src($row->ID, 'thumbnail');
        echo "<li>ID: <b>$row->ID</b> | Title: $row->post_title <br>GUID: $row->guid <br>";
        if ($img) echo "<img src='{$img[0]}' style='max-width:100px'><br>";
        echo "</li><hr>";
    }
    echo "</ul>";
} else {
    echo "No matches found.";
}
?>
