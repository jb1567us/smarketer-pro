<?php
// force_delete_template.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
$dir = get_stylesheet_directory();
$file = $dir . '/page.php';

if (file_exists($file)) {
    if (unlink($file)) {
        echo "✅ Deleted page.php. Fallback to index.php should activate.";
    } else {
        echo "❌ Failed to delete page.php";
    }
} else {
    echo "⚠️ page.php does not exist.";
}
?>