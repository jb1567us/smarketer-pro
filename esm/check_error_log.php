<?php
// check_error_log.php
$log = $_SERVER['DOCUMENT_ROOT'] . '/error_log';
if (file_exists($log)) {
    echo "<h1>Error Log Found</h1>";
    echo "<pre>" . htmlspecialchars(file_get_contents($log)) . "</pre>";
} else {
    echo "<h1>No error_log found in root.</h1>";
    // Try php_error.log
    $log2 = $_SERVER['DOCUMENT_ROOT'] . '/php_error.log';
    if (file_exists($log2)) {
        echo "<h1>php_error.log Found</h1>";
        echo "<pre>" . htmlspecialchars(file_get_contents($log2)) . "</pre>";
    }
}
?>