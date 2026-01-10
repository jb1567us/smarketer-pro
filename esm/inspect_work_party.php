<?php
// inspect_work_party.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$title = "Work Party Mulch Series Collage";
$page = get_page_by_title($title, OBJECT, 'page');

if (!$page) {
    // Try slug derived from title
    $slug = sanitize_title($title);
    $page = get_page_by_path($slug, OBJECT, 'page');
}

echo "<h1>Inspecting: $title</h1>";

if ($page) {
    echo "ID: " . $page->ID . "<br>";
    $content = $page->post_content;

    echo "<h3>Raw Content Start (CSS Check):</h3>";
    echo "<textarea style='width:100%;height:150px;'>" . htmlspecialchars(substr($content, 0, 500)) . "</textarea><br>";

    echo "<h3>Links Area (Formatting Check):</h3>";
    // Find "Designer Specifications"
    $pos = strpos($content, 'Designer Specifications');
    if ($pos !== false) {
        echo "<textarea style='width:100%;height:150px;'>" . htmlspecialchars(substr($content, $pos, 800)) . "</textarea><br>";
    } else {
        echo "Designer Specs not found.<br>";
        echo "<textarea style='width:100%;height:150px;'>" . htmlspecialchars(substr($content, -800)) . "</textarea><br>";
    }

    // Check for other pages with Raw CSS?
    global $wpdb;
    $bad_css_count = $wpdb->get_var("SELECT COUNT(*) FROM {$wpdb->posts} WHERE post_content LIKE '/* Font Imports */%' AND post_status='publish'");
    echo "<hr>Total Pages starting with Raw CSS: $bad_css_count<br>";

} else {
    echo "Page not found.";
}
?>