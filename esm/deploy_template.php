<?php
ini_set('display_errors', 1);
error_reporting(E_ALL);

$source = $_SERVER['DOCUMENT_ROOT'] . '/esm-artwork-template.php';
$dest = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/mu-plugins/esm-artwork-template.php';

echo "<h1>Deploying Template</h1>";
if (!file_exists($source)) {
    die("Source file not found at $source");
}

if (copy($source, $dest)) {
    echo "SUCCESS: Copied to $dest<br>";
    echo "Size: " . filesize($dest) . " bytes";
} else {
    echo "FAILURE: Could not copy to $dest";
}
?>
