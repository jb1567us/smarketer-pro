<?php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$page = get_page_by_path('animal-kingdom', OBJECT, 'page');
if ($page) {
    echo "<h1>Content of Animal Kingdom</h1>";
    echo "<textarea style='width:100%;height:500px;'>" . htmlspecialchars($page->post_content) . "</textarea>";

    echo "<h2>1. Check for Schema Leak</h2>";
    // Look for the boundary between CSS and Schema
    $leak_pos = strpos($page->post_content, 'TRADE ONLY');
    if ($leak_pos !== false) {
        echo "<pre>" . htmlspecialchars(substr($page->post_content, $leak_pos - 100, 500)) . "</pre>";
    } else {
        echo "Could not find 'TRADE ONLY' string.";
    }

    echo "<h2>2. Check for Duplicate High Res Links</h2>";
    // Look for all occurrences of "High Res"
    preg_match_all('/<a[^>]*>.*?High Res.*?<\/a>/i', $page->post_content, $matches);
    echo "<pre>" . print_r($matches[0], true) . "</pre>";

    echo "<h2>3. Full Raw Content (First 2000 chars)</h2>";
    echo "<textarea style='width:100%;height:300px;'>" . htmlspecialchars(substr($page->post_content, 0, 2000)) . "</textarea>";
} else {
    echo "Page not found.";
}
?>