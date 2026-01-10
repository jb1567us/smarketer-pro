<?php
// diagnose_theme_crash.php
// Robust error trapping to find why esm-portfolio faults

// Turn up error reporting to maximum
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

// Define shutdown function to catch fatal errors (E_ERROR)
register_shutdown_function(function () {
    $error = error_get_last();
    if ($error && ($error['type'] === E_ERROR || $error['type'] === E_PARSE || $error['type'] === E_COMPILE_ERROR)) {
        echo "<div style='background:red;color:white;padding:20px;margin:20px;border:3px solid black;'>";
        echo "<h1>💀 FATAL CRASH DETECTED</h1>";
        echo "<strong>Message:</strong> " . $error['message'] . "<br>";
        echo "<strong>File:</strong> " . $error['file'] . "<br>";
        echo "<strong>Line:</strong> " . $error['line'] . "<br>";
        echo "</div>";
    }
    echo "<h2>🏁 Script Finished (Shutdown)</h2>";
});

echo "<h1>🔍 Diagnosing Theme Crash</h1>";
echo "Current Time: " . date('H:i:s') . "<br>";

$theme_dir = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/themes/esm-portfolio';

if (!is_dir($theme_dir)) {
    die("❌ Theme directory not found: $theme_dir");
}

echo "Theme Directory Exists: $theme_dir<br>";

// 1. Check file permissions/existence
$critical = ['style.css', 'index.php', 'functions.php', 'header.php', 'footer.php', 'page.php'];
foreach ($critical as $file) {
    if (file_exists("$theme_dir/$file")) {
        echo "✅ Found $file (" . filesize("$theme_dir/$file") . " bytes)<br>";
    } else {
        echo "⚠️ Missing $file<br>";
    }
}

// 2. Try to include functions.php directly
echo "<h3>🧪 Attempting to include functions.php...</h3>";
// Mock WordPress basic functions if needed to prevent 'call to undefined function'
if (!function_exists('add_action')) {
    echo "⚠️ WordPress environment not loaded fully? (Should be if run via browser)<br>";
} else {
    echo "Context: WordPress functions available.<br>";
}

// Check for syntax errors before include using php -l equivalent? No, too complex.
// Just include inside try/catch (won't catch Parse Error, but shutdown handler will).

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php'); // Ensure WP loaded

try {
    include("$theme_dir/functions.php");
    echo "✅ include('functions.php') completed successfully.<br>";
} catch (Throwable $t) {
    echo "<div style='background:orange;color:black;padding:10px;'>";
    echo "💥 Exception caught during include: " . $t->getMessage() . "<br>";
    echo "File: " . $t->getFile() . ":" . $t->getLine();
    echo "</div>";
}

echo "<h3>🏁 Diagnosis Complete (if you see this)</h3>";
?>