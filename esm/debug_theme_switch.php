<?php
// debug_theme_switch.php
// Try to switch theme and show errors
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$target = 'esm-portfolio';
echo "<h1>Debug Theme Switch</h1>";
echo "Current: " . get_option('stylesheet') . "<br>";

// Validate target
if (!is_dir(WP_CONTENT_DIR . '/themes/' . $target)) {
    die("❌ Target theme dir missing.");
}

// Switch
update_option('template', $target);
update_option('stylesheet', $target);

echo "New: " . get_option('stylesheet') . "<br>";

// Test load of functions.php
$funcs = WP_CONTENT_DIR . '/themes/' . $target . '/functions.php';
if (file_exists($funcs)) {
    echo "Testing functions.php inclusion...<br>";
    try {
        include_once($funcs);
        echo "✅ functions.php loaded without fatal error.<br>";
    } catch (Throwable $e) {
        echo "❌ FATAL ERROR in functions.php: " . $e->getMessage() . "<br>";
    }
} else {
    echo "⚠️ functions.php missing.<br>";
}
echo "<h2>Check site now.</h2>";
?>