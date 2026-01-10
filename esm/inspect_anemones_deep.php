<?php
// inspect_anemones_deep.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$slug = 'anemones';
$page = get_page_by_path($slug, OBJECT, 'page');

if (!$page) {
    global $wpdb;
    $row = $wpdb->get_row("SELECT ID, post_title, post_content FROM {$wpdb->posts} WHERE post_name LIKE '%anemones%' LIMIT 1");
    $page = $row;
}

echo "<h1>Deep Inspect: " . $page->post_title . "</h1>";
$content = $page->post_content;

// Show the first 5000 chars safely
echo "<textarea style='width:100%;height:400px;font-family:monospace;'>" . htmlspecialchars($content) . "</textarea>";

// specifically show around the </style>
$pos = strpos($content, '</style>');
if ($pos !== false) {
    echo "<h3>Around Closing Tag ($pos):</h3>";
    echo "<pre>" . htmlspecialchars(substr($content, $pos - 100, 200)) . "</pre>";
} else {
    echo "<h3>NO Closing Style Tag Found!</h3>";
}
?>