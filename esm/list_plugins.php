<?php
// list_plugins.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
$dir = WP_CONTENT_DIR . '/plugins';

if (file_exists($dir)) {
    echo "<h1>Active Plugins</h1><ul>";
    $scan = scandir($dir);
    foreach ($scan as $f) {
        if ($f == '.' || $f == '..')
            continue;
        if (is_dir($dir . '/' . $f)) {
            echo "<li>$f</li>";
        }
    }
    echo "</ul>";
} else {
    echo "Plugins folder missing via WP_CONTENT_DIR";
}
?>