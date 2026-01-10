<?php
// inspect_theme.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$dir = get_stylesheet_directory();
$file = $dir . '/page.php';

echo "<h1>Inspecting: $file</h1>";

if (file_exists($file)) {
    echo "<h3>Content:</h3>";
    echo "<textarea style='width:100%;height:500px;'>";
    echo htmlspecialchars(file_get_contents($file));
    echo "</textarea>";
} else {
    echo "❌ File not found.<br>";
    echo "<h3>Dir Scan:</h3><ul>";
    $scan = scandir($dir);
    foreach ($scan as $f) {
        echo "<li>$f</li>";
    }
    echo "</ul>";
}
?>