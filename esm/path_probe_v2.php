<?php
echo "Current File: " . __FILE__ . "<br>";
echo "Document Root: " . $_SERVER['DOCUMENT_ROOT'] . "<br>";

$candidates = [
    '/home/elliotspencermor/public_html/content/plugins/esm-trade-portal/esm-trade-portal.php',
    '/home/elliotspencermor/public_html/wp-content/plugins/esm-trade-portal/esm-trade-portal.php',
    dirname(__FILE__) . '/content/plugins/esm-trade-portal/esm-trade-portal.php',
    dirname(__FILE__) . '/wp-content/plugins/esm-trade-portal/esm-trade-portal.php'
];

foreach ($candidates as $path) {
    echo "Path: " . $path . " => " . (file_exists($path) ? "EXISTS" : "NOT FOUND") . "<br>";
    if (file_exists($path)) {
        echo "Writable? " . (is_writable($path) ? "YES" : "NO") . "<br>";
    }
}
?>
