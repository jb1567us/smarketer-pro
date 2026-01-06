<?php
// diagnose_blank.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

// Target the page from the screenshot: "anemones"
$slug = 'anemones';
$page = get_page_by_path($slug, OBJECT, 'page');

if (!$page) {
    // Try fuzzy search if slug mismatch
    global $wpdb;
    $row = $wpdb->get_row("SELECT ID, post_title, post_content FROM {$wpdb->posts} WHERE post_name LIKE '%anemones%' LIMIT 1");
    if ($row) {
        $page = $row;
        echo "Found via fuzzy search: " . $page->post_title . "<br>";
    } else {
        die("Page 'anemones' not found.");
    }
}

echo "<h1>Diagnosing: " . $page->post_title . "</h1>";
$content = $page->post_content;

echo "<h3>First 2000 chars (Escaped):</h3>";
echo "<pre style='background:#ddd; padding:10px; white-space:pre-wrap;'>" . htmlspecialchars(substr($content, 0, 2000)) . "</pre>";

// Check for unclosed style
$styleCount = substr_count($content, '<style>');
$closeStyleCount = substr_count($content, '</style>');

echo "<h3>Analysis:</h3>";
echo "Open <style> tags: $styleCount<br>";
echo "Close </style> tags: $closeStyleCount<br>";

if ($styleCount > $closeStyleCount) {
    echo "<h2 style='color:red;'>CRITICAL: Unclosed <style> tag detected!</h2>";
    echo "This explains why the page is blank. The browser thinks the HTML is CSS.";
} else {
    echo "Style tags seem balanced. Checking for other hiding mechanisms...<br>";
    if (strpos($content, 'display: none') !== false) {
        echo "Found 'display: none'<br>";
    }
}
?>