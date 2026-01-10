<?php
// kill_functions_again.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
$dir = get_stylesheet_directory();
$src = $dir . '/functions.php';
$dst = $dir . '/functions.php.bak2';

if (rename($src, $dst)) {
    echo "✅ Renamed functions.php to .bak2";
} else {
    echo "❌ Failed to rename functions.php";
}
?>