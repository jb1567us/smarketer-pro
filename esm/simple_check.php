<?php
// simple_check.php
echo "<h1>System Check</h1>";
echo "PHP Version: " . phpversion() . "<br>";
echo "Current Dir: " . __DIR__ . "<br>";

if (class_exists('ZipArchive')) {
    echo "✅ ZipArchive AVAILABLE<br>";
} else {
    echo "❌ ZipArchive MISSING<br>";
}

$zip = __DIR__ . '/esm-deploy.zip';
if (file_exists($zip)) {
    echo "✅ Zip File Found: $zip (" . filesize($zip) . " bytes)<br>";
} else {
    echo "❌ Zip File NOT Found in " . __DIR__ . "<br>";
    $files = scandir(__DIR__);
    echo "Files here:<br>";
    foreach ($files as $f) {
        if (strpos($f, 'zip') !== false)
            echo "$f<br>";
    }
}
?>