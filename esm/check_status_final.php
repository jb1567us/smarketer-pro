<?php
require_once('wp-load.php');
global $wpdb;
$pid = 1927;

// Force clear cache for this post just in case
clean_post_cache($pid);

// Read via SQL (Bypass Object Cache)
$row = $wpdb->get_row("SELECT post_content FROM $wpdb->posts WHERE ID = $pid");
$c = $row->post_content;

echo "<h1>Final Check (SQL Read) for Portal ($pid)</h1>";

// Check for Style Tag
if (strpos($c, '<style>/* Font Imports */') !== false) {
    echo "✅ CSS IS WRAPPED in &lt;style&gt;<br>";
} else {
    echo "❌ CSS IS NOT WRAPPED<br>";
}

// Check for Script Tag
if (strpos($c, '<script type="application/ld+json">') !== false) {
    echo "✅ JSON IS WRAPPED in &lt;script&gt;<br>";
} else {
    echo "❌ JSON IS NOT WRAPPED<br>";
}

echo "<h3>Preview (First 800 chars):</h3>";
echo "<pre>" . htmlspecialchars(substr($c, 0, 800)) . "</pre>";
echo "<hr>";

$marker = strpos($c, 'VisualArtwork Schema');
if ($marker) {
    echo "<h3>JSON Part (Around Schema):</h3>";
    echo "<pre>" . htmlspecialchars(substr($c, $marker, 500)) . "</pre>";
}
?>