<?php
// debug_path.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

echo "<h1>Debug Path</h1>";

$filename = 'Red_PlanetPainting.jpg';
$dirs = [
    $_SERVER['DOCUMENT_ROOT'] . '/wp-content/uploads/2025/11/',
    $_SERVER['DOCUMENT_ROOT'] . '/wp-content/uploads/2025/11-holdingspace-originals/',
    $_SERVER['DOCUMENT_ROOT'] . '/uploads/2025/11/',
    ABSPATH . 'wp-content/uploads/2025/11/'
];

foreach ($dirs as $d) {
    echo "Checking dir: $d<br>";
    if (is_dir($d)) {
        echo "✅ Is Dir.<br>";
        $f = $d . $filename;
        if (file_exists($f)) {
            echo "✅✅✅ FILE FOUND: $f<br>";
        } else {
            echo "❌ File Missing: $filename<br>";
        }
    } else {
        echo "❌ Not a Dir.<br>";
    }
    echo "<hr>";
}
?>