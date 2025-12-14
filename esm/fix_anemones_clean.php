<?php
// fix_anemones_clean.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
global $wpdb;

$slug = 'anemones';
$row = $wpdb->get_row("SELECT ID, post_content FROM {$wpdb->posts} WHERE post_name='$slug'");
if (!$row)
    die("Page not found");

$content = $row->post_content;
echo "Original Length: " . strlen($content) . "<br>";

// 1. Remove Block Comments
$content = str_replace('<!-- wp:html -->', '', $content);
$content = str_replace('<!-- /wp:html -->', '', $content);
echo "Stripped Block Comments.<br>";

// 2. Identify Split Point
$split = '<div class="artwork-page-container"';
$pos = strpos($content, $split);

if ($pos !== false) {
    $head = substr($content, 0, $pos);
    $body = substr($content, $pos);

    // 3. Clean Head
    // Strip tags to get raw CSS? 
    // The head currently contains: <style> ... </style> (maybe) and some comments and JSON.
    // Let's just FORCE formatting.
    // Remove all <style> and </style> from head
    $cleanHead = str_replace(['<style>', '</style>'], '', $head);

    // Now wrap it
    $newHead = "<style>\n" . trim($cleanHead) . "\n</style>\n";

    // Reassemble
    $newContent = $newHead . $body;

    $wpdb->update($wpdb->posts, ['post_content' => $newContent], ['ID' => $row->ID]);
    echo "✅ Updated Anemones. New Length: " . strlen($newContent);

} else {
    echo "❌ Could not find Split Point (artwork-page-container). Content might be totally broken.";
}
?>