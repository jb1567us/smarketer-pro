<?php
// emergency_restore.php
// Disables ALL MU-Plugins to fix Critical Error

$mu_dir = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/mu-plugins';
echo "<h1>🚑 Emergency Rescue</h1>";

if (is_dir($mu_dir)) {
    $files = glob($mu_dir . '/*.php');
    if ($files) {
        foreach ($files as $file) {
            $new_name = $file . '.off';
            if (rename($file, $new_name)) {
                echo "✅ Disabled: " . basename($file) . "<br>";
            } else {
                echo "❌ Failed to disable: " . basename($file) . "<br>";
            }
        }
    } else {
        echo "No PHP files found in MU-Plugins.<br>";
    }
} else {
    echo "MU-Plugins directory not found.<br>";
}

// Also check for error_log in root
$error_log = $_SERVER['DOCUMENT_ROOT'] . '/error_log';
if (file_exists($error_log)) {
    echo "<h2>📜 Last 5 Errors:</h2>";
    $lines = file($error_log);
    $last = array_slice($lines, -5);
    foreach ($last as $l) {
        echo "<pre>$l</pre>";
    }
}

if (function_exists('opcache_reset')) {
    opcache_reset();
    echo "✅ OpCache Reset.<br>";
}

echo "<a href='/fireworks/'>Try /fireworks/</a>";
?>