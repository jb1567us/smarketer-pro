<?php
// switch_theme_emergency.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
$target = 'twentytwentyfour';

if (!is_dir(WP_CONTENT_DIR . '/themes/' . $target)) {
    // Try simpler one if 2024 missing
    $target = 'twentytwentythree';
}

echo "<h1>Switching to $target</h1>";

update_option('template', $target);
update_option('stylesheet', $target);

echo "New Template: " . get_option('template') . "<br>";
echo "New Stylesheet: " . get_option('stylesheet') . "<br>";
echo "<h3>IF THIS WORKS, THE SITE WILL BE UGLY BUT VISIBLE.</h3>";
?>