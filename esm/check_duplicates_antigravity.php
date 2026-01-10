<?php
// Load WordPress
require_once('wp-load.php');

// Get all pages
$args = array(
    'post_type' => 'page',
    'posts_per_page' => -1,
    'post_status' => array('publish', 'draft', 'pending', 'private', 'future')
);

$query = new WP_Query($args);
$pages = $query->posts;

$titles = array();
$duplicates = array();

foreach ($pages as $page) {
    $title = trim($page->post_title);
    $data = array(
        'id' => $page->ID,
        'title' => $title,
        'slug' => $page->post_name,
        'date' => $page->post_date,
        'status' => $page->post_status,
        'link' => get_permalink($page->ID)
    );

    if (isset($titles[$title])) {
        // If this is the first duplicate found for this title, add the original to the list
        if (!isset($duplicates[$title])) {
            $duplicates[$title] = array();
            $duplicates[$title][] = $titles[$title];
        }
        $duplicates[$title][] = $data;
    } else {
        $titles[$title] = $data;
    }
}

// Convert to list for JSON
$result = array();
foreach ($duplicates as $title => $items) {
    $result[] = array(
        'title' => $title,
        'count' => count($items),
        'items' => $items
    );
}

header('Content-Type: application/json');
echo json_encode(array(
    'total_pages_scanned' => count($pages),
    'duplicate_sets_found' => count($result),
    'duplicates' => $result
), JSON_PRETTY_PRINT);
?>
