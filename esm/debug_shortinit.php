<?php
// debug_shortinit.php
define('SHORTINIT', true);
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

echo "<h1>⚡ ShortInit Debug</h1>";

global $wpdb;
if ($wpdb) {
    echo "✅ DB Connected.<br>";
    $row = $wpdb->get_row("SELECT * FROM $wpdb->posts WHERE ID = 213");
    if ($row) {
        echo "Found Post: " . $row->post_title . "<br>";
        echo "Slug: " . $row->post_name . "<br>";
        echo "Status: " . $row->post_status . "<br>";
    } else {
        echo "❌ Post 213 not found.";
    }
} else {
    echo "❌ DB Object Failure.";
}
?>