<?php
// activate_theme_force.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$target = 'esm-portfolio';

// Check if theme exists
if (!is_dir(WP_CONTENT_DIR . '/themes/' . $target)) {
    die("❌ Theme directory $target not found.");
}

// Force Update options
update_option('template', $target);
update_option('stylesheet', $target);

// Clear any caches
if (function_exists('wp_cache_flush'))
    wp_cache_flush();

echo "<h1>Theme Activated: " . get_option('stylesheet') . "</h1>";
echo "Current Template: " . get_option('template') . "<br>";
?>