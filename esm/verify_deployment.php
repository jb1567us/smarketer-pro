<?php
$files = [
    'content/plugins/esm-trade-portal/esm-trade-portal.php',
    'wp-content/plugins/esm-trade-portal/esm-trade-portal.php',
    'content/plugins/esm-trade-portal/esm-trade-portal.js',
    'wp-content/plugins/esm-trade-portal/esm-trade-portal.js'
];

foreach ($files as $file) {
    echo "<h2>File: $file</h2>";
    $path = __DIR__ . '/' . $file;
    if (file_exists($path)) {
        echo "MD5: " . md5_file($path) . "<br>";
        echo "First 100 chars: <pre>" . htmlspecialchars(substr(file_get_contents($path), 0, 100)) . "</pre><br>";
        echo "Last 100 chars: <pre>" . htmlspecialchars(substr(file_get_contents($path), -100)) . "</pre><br>";
    } else {
        echo "NOT FOUND<br>";
    }
}
?>
