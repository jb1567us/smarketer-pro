<?php
// kill_theme_functions.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
$dir = get_stylesheet_directory();
$src = $dir . '/functions.php';
$dst = $dir . '/functions.php.bak';

if (file_exists($src)) {
    if (rename($src, $dst)) {
        echo "✅ Renamed functions.php to .bak";
    } else {
        echo "❌ Failed to rename functions.php";
    }
} else {
    echo "⚠️ functions.php not found";
}
?>