<?php
// debug_header_failure.php
// Inspect the header template raw content to check for Base64 corruption
// and verify Navigation ID.

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
header('Content-Type: text/plain');

echo "--- NAVIGATION DIAGNOSTIC ---\n";
$nav = get_page_by_path('main-navigation', OBJECT, 'wp_navigation');
if ($nav) {
    echo "Navigation Found: ID " . $nav->ID . "\n";
    echo "Content Snippet:\n" . substr($nav->post_content, 0, 100) . "...\n";
} else {
    echo "❌ CRITICAL: 'main-navigation' post NOT found.\n";
}

echo "\n--- HEADER TEMPLATE INSPECTION ---\n";
$headers = get_posts([
    'post_type' => 'wp_template_part',
    'post_status' => 'any',
    'numberposts' => -1,
    'tax_query' => [['taxonomy' => 'wp_template_part_area', 'field' => 'slug', 'terms' => 'header']]
]);

foreach ($headers as $h) {
    echo "ID: " . $h->ID . " | Slug: " . $h->post_name . "\n";
    echo "Length: " . strlen($h->post_content) . " bytes\n";
    echo "Has Base64? " . (strpos($h->post_content, 'base64') !== false ? "YES" : "NO") . "\n";
    echo "Has Nav Ref? " . (strpos($h->post_content, '"ref":') !== false ? "YES" : "NO") . "\n";

    // Dump the first 500 chars to check structure
    echo "Start of Content:\n";
    echo substr($h->post_content, 0, 500) . "\n...\n";
    echo "--------------------------------------------------\n";
}
?>