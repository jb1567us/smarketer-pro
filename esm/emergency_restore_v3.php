<?php
// emergency_restore_v3.php
// Minimal diagnostic script to find the crash cause

$log_file = $_SERVER['DOCUMENT_ROOT'] . '/error_log';

echo "<h1>🚑 Diagnostics V3</h1>";

if (file_exists($log_file)) {
    echo "<h2>📜 Last 30 Errors:</h2>";
    $lines = file($log_file);
    $last = array_slice($lines, -30);
    foreach ($last as $l) {
        echo "<pre style='background:#f0f0f0; border:1px solid #ccc; padding:5px; margin:2px;'>" . htmlspecialchars($l) . "</pre>";
    }
} else {
    echo "No error_log found in root.<br>";
}

echo "System Time: " . date('Y-m-d H:i:s');
?>