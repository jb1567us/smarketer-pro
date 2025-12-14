<?php
// debug_server_simple.php
error_reporting(E_ALL);
ini_set('display_errors', 1);

echo "<h1>Primitive Server Diag</h1>";
echo "Current Dir: " . getcwd() . "<br>";

echo "<h3>Scandir .</h3><ul>";
$scan = scandir('.');
foreach ($scan as $f) {
    echo "<li>$f</li>";
}
echo "</ul>";

$testFile = 'wp-config.php';
echo "<h3>Testing $testFile</h3>";
if (file_exists($testFile)) {
    echo "EXISTS.<br>";
    echo "Size: " . filesize($testFile) . "<br>";
    echo "Readable: " . (is_readable($testFile) ? 'YES' : 'NO') . "<br>";
} else {
    echo "NOT FOUND.<br>";
}

echo "<h3>Testing Theme Dir</h3>";
$themeDir = 'wp-content/themes/esm-portfolio';
if (is_dir($themeDir)) {
    echo "THEME DIR EXISTS.<br>";
    $scan = scandir($themeDir);
    foreach ($scan as $f) {
        echo "<li>$f</li>";
    }
} else {
    echo "THEME DIR NOT FOUND at $themeDir<br>";
}
?>