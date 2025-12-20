<?php
ini_set('display_errors', 1);
error_reporting(E_ALL);

echo "<h1>Deployment v2</h1>";

$wp_load = $_SERVER['DOCUMENT_ROOT'] . '/wp-load.php';
require_once($wp_load);

if (!defined('WPMU_PLUGIN_DIR')) {
    echo "WPMU_PLUGIN_DIR not defined, defining it...<br>";
    define('WPMU_PLUGIN_DIR', WP_CONTENT_DIR . '/mu-plugins');
}

$dest_dir = WPMU_PLUGIN_DIR;
echo "Dest Dir: $dest_dir<br>";


// Deploy artwork_data.json
$source_json = $_SERVER['DOCUMENT_ROOT'] . '/artwork_data.json';
$dest_json = $dest_dir . '/artwork_data.json';

if (!file_exists($source_json)) {
    die("Source JSON NOT FOUND: $source_json");
}

if (file_exists($dest_json)) {
    if (unlink($dest_json)) {
        echo "Deleted old JSON.<br>";
    } else {
        echo "Failed to delete old JSON.<br>";
    }
}

if (copy($source_json, $dest_json)) {
    echo "<h1>SUCCESS: MOVED JSON.</h1>";
    echo "Size: " . filesize($dest_json);
} else {
    echo "<h1>FAIL: JSON Copy failed.</h1>";
    print_r(error_get_last());
}
?>
