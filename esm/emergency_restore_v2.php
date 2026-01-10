<?php
// emergency_restore_v2.php
// Disables the likely culprit and reads logs

$mu_file = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/mu-plugins/esm-design-system.php';
$log_file = $_SERVER['DOCUMENT_ROOT'] . '/error_log';

echo "<h1>🚑 Emergency Rescue V2</h1>";

// 1. Disable the plugin
if (file_exists($mu_file)) {
    if (rename($mu_file, $mu_file . '.off')) {
        echo "✅ Disabled: esm-design-system.php<br>";
    } else {
        echo "❌ Failed to disable: esm-design-system.php<br>";
    }
} else {
    echo "⚠️ esm-design-system.php not found (maybe already disabled?)<br>";
}

// 2. Read Logs
if (file_exists($log_file)) {
    echo "<h2>📜 Recent Errors:</h2>";
    $lines = file($log_file);
    $last = array_slice($lines, -50); // Get more context
    foreach ($last as $l) {
        echo "<pre>" . htmlspecialchars($l) . "</pre>";
    }
} else {
    echo "No error_log found in root.<br>";
}

// 3. Flush
if (function_exists('opcache_reset'))
    opcache_reset();
echo "<a href='/fireworks/'>Try /fireworks/</a>";
?>