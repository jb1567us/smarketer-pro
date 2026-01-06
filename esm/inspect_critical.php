<?php
// inspect_critical.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$themeDir = get_stylesheet_directory();
$muDir = WPMU_PLUGIN_DIR;

$files = [
    'header.php' => $themeDir . '/header.php',
    'footer.php' => $themeDir . '/footer.php',
    'functions.php' => $themeDir . '/functions.php',
    'rescue.php' => $muDir . '/rescue.php'
];

foreach ($files as $name => $path) {
    echo "<h2>Checking $name</h2>";
    if (file_exists($path)) {
        echo "Path: $path (Size: " . filesize($path) . " bytes)<br>";
        echo "<div id='b64_$name'>";
        echo base64_encode(file_get_contents($path));
        echo "</div>";
    } else {
        echo "❌ File not found at $path<br>";
    }
    echo "<hr>";
}
?>