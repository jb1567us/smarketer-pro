<?php
// Recursively find esm-artwork-template.php
$dir = new RecursiveDirectoryIterator('wp-content');
$iterator = new RecursiveIteratorIterator($dir);
foreach ($iterator as $file) {
    if ($file->getFilename() == 'esm-artwork-template.php') {
        echo "FOUND: " . $file->getPathname() . "\n";
    }
}
echo "Search complete.\n";
