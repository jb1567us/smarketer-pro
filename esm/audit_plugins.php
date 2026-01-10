
<?php
// audit_plugins.php
require_once('wp-load.php');
echo "<pre>AUDIT START\n";

// 1. Active Plugins
$active = get_option('active_plugins');
echo "Active Plugins:\n";
print_r($active);

// 2. MU Plugins
$mu = get_mu_plugins();
echo "MU Plugins:\n";
print_r($mu);

// 3. File Scan
echo "\nScanning wp-content/plugins/ for 'esm-trade-portal.php':\n";
$iter = new RecursiveIteratorIterator(
    new RecursiveDirectoryIterator('wp-content/plugins/', RecursiveDirectoryIterator::SKIP_DOTS),
    RecursiveIteratorIterator::SELF_FIRST,
    RecursiveIteratorIterator::CATCH_GET_CHILD
);

foreach ($iter as $path => $dir) {
    if ($dir->isFile() && $dir->getFilename() === 'esm-trade-portal.php') {
        echo "FOUND: $path\n";
        echo "Size: " . filesize($path) . "\n";
        $c = file_get_contents($path);
        if (strpos($c, 'V2 DEBUG ACTIVE') !== false) echo "  Status: V2 (DEBUG FOUND)\n";
        else echo "  Status: V1 or OLD\n";
    }
}

echo "\nScanning wp-content/mu-plugins/:\n";
if (is_dir('wp-content/mu-plugins/')) {
    $iter_mu = new RecursiveIteratorIterator(
        new RecursiveDirectoryIterator('wp-content/mu-plugins/', RecursiveDirectoryIterator::SKIP_DOTS)
    );
    foreach ($iter_mu as $path => $dir) {
        if ($dir->isFile()) {
            echo "FILE: $path\n";
             if ($dir->getFilename() === 'esm-trade-portal.php') {
                 echo "  !!! CRITICAL MATCH !!!\n";
             }
        }
    }
}

echo "AUDIT END</pre>";
?>
