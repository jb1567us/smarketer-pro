<?php
// debug_raw_sql.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
global $wpdb;

echo "<h1>🛠 Raw SQL Debug</h1>";

$results = $wpdb->get_results("SELECT ID, post_title, post_name, post_status FROM $wpdb->posts WHERE ID = 213");

if ($results) {
    echo "Found " . count($results) . " row(s).<br>";
    foreach ($results as $row) {
        echo "ID: " . $row->ID . "<br>";
        echo "Title: " . $row->post_title . "<br>";
        echo "Slug: " . $row->post_name . "<br>";
        echo "Status: " . $row->post_status . "<br>";
    }
} else {
    echo "❌ No results in SQL.";
}
?>