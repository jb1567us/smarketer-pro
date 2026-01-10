<?php
// live_debug.php
ini_set('display_errors', 1);
error_reporting(E_ALL);

echo "<h1>✅ Connectivity Confirmed</h1>";
echo "<p>This script is running successfully on your server.</p>";
echo "<hr>";

echo "<h3>Server Info:</h3>";
echo "<b>PHP Version:</b> " . phpversion() . "<br>";
echo "<b>Current Directory:</b> " . __DIR__ . "<br>";

echo "<h3>File Check:</h3>";
$files = ['wp-config.php', 'wp-settings.php', 'wp-load.php', 'wp-admin', 'wp-includes'];
foreach ($files as $f) {
    if (file_exists($f)) {
        echo "✅ Found: $f<br>";
    } else {
        echo "❌ MISSING: $f<br>";
    }
}

echo "<h3>WordPress Check:</h3>";
if (file_exists('wp-config.php')) {
    echo "Attempting to read wp-config.php... ";
    $config = file_get_contents('wp-config.php');
    if (strpos($config, "wp-settings.php") !== false) {
        echo "Logic seems correct.<br>";
    } else {
        echo "⚠️ wp-settings.php NOT included in config!<br>";
    }
}
?>
