<?php
// copy_functions_out.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
$src = get_stylesheet_directory() . '/functions.php';
$dst = $_SERVER['DOCUMENT_ROOT'] . '/funcs_dump.txt';

if (copy($src, $dst)) {
    echo "<h1>Copied functions.php to funcs_dump.txt</h1>";
    echo "Size: " . filesize($dst);
} else {
    echo "<h1>Failed to copy. Source exists? " . (file_exists($src) ? 'Yes' : 'No') . "</h1>";
}
?>