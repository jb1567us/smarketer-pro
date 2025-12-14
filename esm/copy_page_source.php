<?php
// copy_page_source.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$dir = get_stylesheet_directory();
$source = $dir . '/page.php';
$dest = $_SERVER['DOCUMENT_ROOT'] . '/temp_page.txt';

echo "Source Path: $source<br>";

if (file_exists($source)) {
    if (copy($source, $dest)) {
        echo "Copied successfully to temp_page.txt";
    } else {
        echo "Failed to copy.";
    }
} else {
    echo "Source not found at $source";
}
?>