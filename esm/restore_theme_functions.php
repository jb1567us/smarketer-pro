<?php
// restore_theme_functions.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
$dir = get_stylesheet_directory();
$src = $dir . '/functions.php.bak';
$dst = $dir . '/functions.php';

if (file_exists($src)) {
    if (rename($src, $dst)) {
        echo "✅ Restored functions.php";
    } else {
        echo "❌ Failed to restore functions.php";
    }
} else {
    echo "⚠️ functions.php.bak not found";
}
?>