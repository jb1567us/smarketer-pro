<?php
// inspect_db_content.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
global $wpdb;
$id = 213;

$row = $wpdb->get_row("SELECT post_content FROM {$wpdb->posts} WHERE ID = $id");
if (!$row)
    die("ID $id not found");

$content = $row->post_content;
echo "<h1>DB Content Inspection (ID $id)</h1>";
echo "Raw Length: " . strlen($content) . "<br>";
echo "Raw Preview: <pre>" . htmlspecialchars(substr($content, 0, 300)) . "</pre><br>";

// Manual Filter Test
echo "<h3>Applying 'the_content' Filter...</h3>";
// Disable plugins is active on filesystem level, so only Core + Theme filters run.
$filtered = apply_filters('the_content', $content);
echo "Filtered Length: " . strlen($filtered) . "<br>";
echo "Filtered Preview: <pre>" . htmlspecialchars(substr($filtered, 0, 300)) . "</pre><br>";

// Output Buffering Check
echo "OB Level: " . ob_get_level() . "<br>";
?>