<?php
// STATIC BYPASS WRAPPER v6
if (isset($_SERVER['REQUEST_URI']) && strpos($_SERVER['REQUEST_URI'], '/anemones/') !== false) {
    header("Cache-Control: no-cache, must-revalidate");
    readfile(__DIR__ . '/anemones_v6.html');
    exit;
}
require(__DIR__ . '/index_wp.php');
?>