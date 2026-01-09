<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

// Attempt to load WordPress environment
echo "<h2>Debug Start</h2>";

if (file_exists('wp-load.php')) {
    define( 'WP_DEBUG', true );
    define( 'WP_DEBUG_DISPLAY', true );
    try {
        require_once('wp-load.php');
        echo "<p>WordPress Loaded Successfully</p>";
    } catch (Throwable $t) {
        echo "<p>Fatal Error during WP Load: " . $t->getMessage() . "</p>";
        echo "<p>File: " . $t->getFile() . " on line " . $t->getLine() . "</p>";
        echo "<pre>" . $t->getTraceAsString() . "</pre>";
    }
} else {
    echo "wp-load.php not found";
}
echo "<h2>Debug End</h2>";
