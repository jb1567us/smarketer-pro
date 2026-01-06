<?php
// verify_fix_final.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$slug = 'anemones';
$page = get_page_by_path($slug, OBJECT, 'page');

if (!$page) {
    global $wpdb;
    $row = $wpdb->get_row("SELECT ID, post_title, post_content FROM {$wpdb->posts} WHERE post_name LIKE '%anemones%' LIMIT 1");
    $page = $row;
}

echo "<h1>Verify Fix: " . $page->post_title . "</h1>";
$content = $page->post_content;

$styleCount = substr_count($content, '<style>');
$closeStyleCount = substr_count($content, '</style>');

echo "Open: $styleCount | Close: $closeStyleCount<br>";

if ($styleCount == $closeStyleCount) {
    echo "<h2 style='color:green;'>✅ FIXED: Styles are balanced.</h2>";
} else {
    echo "<h2 style='color:red;'>❌ BROKEN: Still unbalanced.</h2>";
}

// Check where it closed
$pos = strpos($content, '</style>');
echo "First closing tag at pos: $pos<br>";
echo "Context: " . htmlspecialchars(substr($content, $pos - 20, 50));
?>