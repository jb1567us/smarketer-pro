<?php
// hide_pieces_of_red.php
header("Content-Type: text/plain");
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$title = "Pieces of Red";
// Use %like% because title might differ slightly (e.g. "Pieces of Red Collage")
global $wpdb;
$page = $wpdb->get_row($wpdb->prepare("SELECT ID, post_title, post_status FROM $wpdb->posts WHERE post_type='page' AND post_title LIKE %s LIMIT 1", '%' . $wpdb->esc_like($title) . '%'));

if (!$page) {
    echo "Error: Could not find page for '$title'.\n";
    exit;
}

echo "Found Page: {$page->post_title} (ID: {$page->ID})\n";
echo "Current Status: {$page->post_status}\n";

$update = array(
    'ID' => $page->ID,
    'post_status' => 'draft'
);

$res = wp_update_post($update);

if (is_wp_error($res) || $res == 0) {
    echo "Error: Failed to update post status.\n";
} else {
    echo "Success: Page set to 'draft'.\n";
}
?>
