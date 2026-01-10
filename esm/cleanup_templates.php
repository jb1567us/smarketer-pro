<?php
// cleanup_templates.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
$dir = get_stylesheet_directory();

$files = ['page.php', 'single.php', 'index.php', 'front-page.php', 'singular.php'];

echo "<h1>Renaming Templates in $dir</h1>";

foreach ($files as $f) {
    $src = $dir . '/' . $f;
    $dst = $dir . '/' . $f . '.bak';

    if (file_exists($src)) {
        if (rename($src, $dst)) {
            echo "✅ Renamed $f to $f.bak<br>";
        } else {
            echo "❌ Failed to rename $f<br>";
        }
    } else {
        echo "⚠️ $f not found<br>";
    }
}
?>