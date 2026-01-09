<?php
// check_themes.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
$dir = WP_CONTENT_DIR . '/themes';

echo "<h1>Themes Available</h1><ul>";
if (file_exists($dir)) {
    $scan = scandir($dir);
    foreach ($scan as $f) {
        if ($f == '.' || $f == '..')
            continue;
        if (is_dir($dir . '/' . $f)) {
            echo "<li>$f</li>";
        }
    }
} else {
    echo "Themes dir not found";
}
echo "</ul>";

echo "<h3>Current Theme</h3>";
echo "Stylesheet: " . get_option('stylesheet') . "<br>";
echo "Template: " . get_option('template') . "<br>";
?>