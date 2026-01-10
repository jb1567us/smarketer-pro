<?php
// restore_theme_final.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
$dir = get_stylesheet_directory(); // This points to CURRENT theme (2024), we need strict path
$themeDir = WP_CONTENT_DIR . '/themes/esm-portfolio';

// 1. Restore functions.php
if (file_exists($themeDir . '/functions.php.bak2')) {
    rename($themeDir . '/functions.php.bak2', $themeDir . '/functions.php');
    echo "✅ Restored functions.php<br>";
} else {
    echo "⚠️ functions.php.bak2 not found (maybe already restored?)<br>";
}

// 2. Switch Theme
update_option('template', 'esm-portfolio');
update_option('stylesheet', 'esm-portfolio');

echo "Active Theme: " . get_option('stylesheet') . "<br>";
echo "<h1>Restoration Complete. Check Site.</h1>";
?>