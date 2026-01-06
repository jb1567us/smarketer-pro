<?php
// find_replacement_images.php
header("Content-Type: text/plain");
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$search_terms = [
    "Right Way",
    "Start Sign",
    "No Public Shrooms",
    "Mushroom Exclamation",
    "Excited Bird"
];

echo "Searching for potential replacement images...\n";

global $wpdb;

foreach ($search_terms as $term) {
    echo "\n--------------------------------------------------\n";
    echo "SEARCHING: '$term'\n";
    
    // Search attachments
    $like = '%' . $wpdb->esc_like($term) . '%';
    $query = $wpdb->prepare(
        "SELECT ID, post_title, guid FROM $wpdb->posts 
         WHERE post_type = 'attachment' 
         AND (post_title LIKE %s OR guid LIKE %s)
         LIMIT 5",
        $like, $like
    );
    
    $results = $wpdb->get_results($query);
    
    if ($results) {
        foreach ($results as $row) {
            echo "MATCH FOUND: ID: $row->ID | Title: $row->post_title | GUID: $row->guid\n";
        }
    } else {
        echo "No matches found.\n";
    }
}
?>
