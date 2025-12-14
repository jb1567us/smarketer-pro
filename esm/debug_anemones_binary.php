<?php
// debug_anemones_binary.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
global $wpdb;

$slug = 'anemones';
$row = $wpdb->get_row("SELECT ID, post_content FROM {$wpdb->posts} WHERE post_name='$slug'");

// Backup content to a transient or file?
// I'll just save it to a temp file on disk for safety.
file_put_contents($_SERVER['DOCUMENT_ROOT'] . '/anemones_backup.html', $row->post_content);

echo "<h1>Replacing Anemones with SIMPLE TEST</h1>";
$simple = "<h1>TESTING VISIBILITY</h1><p>If you see this, content rendering works.</p>";

$wpdb->update($wpdb->posts, ['post_content' => $simple], ['ID' => $row->ID]);
echo "Updated to simple content.";
?>