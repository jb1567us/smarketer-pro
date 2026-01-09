<?php
// inspect_theme_b64.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$dir = get_stylesheet_directory();
$files = ['functions.php', 'wp-config.php']; // Can't read config usually, but try.

foreach ($files as $f) {
    echo "<h2>Checking: $f</h2>";
    $path = $dir . '/' . $f;
    if (file_exists($path)) {
        $size = filesize($path);
        echo "Size: " . $size . " bytes<br>";
        echo "<h3>Base64 Content:</h3>";
        echo "<div id='b64_$f'>";
        echo base64_encode(file_get_contents($path));
        echo "</div>";
    } else {
        echo "❌ File not found.<br>";
    }
    echo "<hr>";
}
?>