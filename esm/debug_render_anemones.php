<?php
// debug_render_anemones.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$slug = 'anemones';
$page = get_page_by_path($slug, OBJECT, 'page');

echo "<h1>Debug Render: Anemones</h1>";
echo "ID: " . $page->ID . "<br>";

$raw = $page->post_content;
echo "<h3>Raw Content (First 100):</h3>";
echo htmlspecialchars(substr($raw, 0, 100)) . "<br>";

// Manual Filter Application
echo "<h3>Applying 'the_content' Filter:</h3>";
try {
    $filtered = apply_filters('the_content', $raw);
    echo "Length: " . strlen($filtered) . "<br>";
    echo "<textarea style='width:100%;height:200px;'>" . htmlspecialchars($filtered) . "</textarea>";
} catch (Exception $e) {
    echo "ERROR during filter: " . $e->getMessage();
}

// Check Caching
if (function_exists('w3tc_flush_all')) {
    w3tc_flush_all();
    echo "<br>Flushed W3TC.";
}
if (function_exists('wp_cache_flush')) {
    wp_cache_flush();
    echo "<br>Flushed Object Cache.";
}
?>