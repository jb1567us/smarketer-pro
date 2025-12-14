<?php
// diagnose_template.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
global $wpdb;

$id = 213; // Anemones
$template = get_post_meta($id, '_wp_page_template', true);
echo "<h1>Template Diagnosis (ID $id)</h1>";
echo "Active Template Meta: [" . ($template ? $template : "default") . "]<br>";

// Get current theme
$theme = wp_get_theme();
echo "Current Theme: " . $theme->get('Name') . " (" . $theme->get_stylesheet() . ")<br>";
echo "Theme Root: " . get_theme_root() . "<br>";
echo "Stylesheet Dir: " . get_stylesheet_directory() . "<br>";

// List files in stylesheet dir to find the template
$dir = get_stylesheet_directory();
$files = scandir($dir);
echo "<h3>Theme Files:</h3><ul>";
foreach ($files as $f) {
    if ($f == '.' || $f == '..')
        continue;
    echo "<li>$f</li>";
}
echo "</ul>";
?>