<?php
// cortex_search_v99.php
header("Content-Type: text/plain");
header("Cache-Control: no-store, no-cache, must-revalidate, max-age=0");

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$search = "In_the_DarkPainting";
echo "SEARCHING FOR: $search\n";

global $wpdb;
$query = "SELECT ID, post_title, guid FROM $wpdb->posts WHERE post_type = 'attachment' AND guid LIKE %s LIMIT 50";
$like = '%' . $wpdb->esc_like($search) . '%';

$results = $wpdb->get_results($wpdb->prepare($query, $like));

if ($results) {
    foreach ($results as $row) {
        $img = wp_get_attachment_image_src($row->ID, 'thumbnail');
        echo "FOUND: ID={$row->ID} | Title={$row->post_title} | GUID={$row->guid}\n";
    }
} else {
    echo "NO MATCHES FOUND.\n";
}
?>
