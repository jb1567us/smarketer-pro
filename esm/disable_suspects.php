<?php
// disable_suspects.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
$dir = WP_CONTENT_DIR . '/plugins';

$suspects = [
    'speedycache',
    'speedycache-pro',
    'wp-optimize',
    'siteseo',
    'siteseo-pro',
    'wordpress-seo'
];

echo "<h1>Disabling Suspects</h1>";

foreach ($suspects as $s) {
    $src = $dir . '/' . $s;
    $dst = $dir . '/' . $s . '.disabled';

    if (file_exists($src)) {
        if (rename($src, $dst)) {
            echo "✅ Disabled $s<br>";
        } else {
            echo "❌ Failed to disable $s<br>";
        }
    } else {
        echo "⚠️ $s not found (or already disabled/renamed)<br>";
    }
}
?>