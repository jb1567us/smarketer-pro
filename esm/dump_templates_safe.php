<?php
// dump_templates_safe.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
$dir = get_stylesheet_directory();

$files = [
    'functions.php',
    'header.php',
    'footer.php',
    'page.php',
    'single.php',
    'index.php'
];

echo "<h1>Safe Template Dump</h1>";

foreach ($files as $f) {
    $path = $dir . '/' . $f;
    echo "<h2>$f</h2>";
    if (file_exists($path)) {
        echo "Size: " . filesize($path) . " bytes<br>";
        echo "<textarea style='width:100%;height:300px;font-family:monospace;'>";
        echo htmlspecialchars(file_get_contents($path));
        echo "</textarea>";
    } else {
        echo "❌ NOT FOUND";
    }
    echo "<hr>";
}
?>