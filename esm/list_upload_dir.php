<?php
// list_upload_dir.php
header("Content-Type: text/plain");
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$upload_dir = wp_upload_dir();
$path = $upload_dir['basedir'] . '/2025/11/';
echo "Listing files in: $path\n\n";

if (is_dir($path)) {
    $files = scandir($path);
    foreach ($files as $file) {
        echo "$file\n";
    }
} else {
    echo "Directory not found.";
}
?>
