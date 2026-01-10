<?php
// dump_functions.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
$path = get_stylesheet_directory() . '/functions.php';
echo "<h1>Functions.php Dump</h1>";
if (file_exists($path)) {
    echo "Size: " . filesize($path) . "<br>";
    echo "B64Start<br>";
    echo base64_encode(file_get_contents($path));
    echo "<br>B64End";
} else {
    echo "Files Missing";
}
?>