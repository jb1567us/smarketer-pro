<?php
echo "Searching for esm-trade-portal.php...\n";
$iterator = new RecursiveIteratorIterator(new RecursiveDirectoryIterator(__DIR__));
foreach ($iterator as $file) {
    if ($file->getFilename() === 'esm-trade-portal.php') {
        echo "PATH: " . $file->getRealPath() . "\n";
    }
}
echo "Done.";
?>
