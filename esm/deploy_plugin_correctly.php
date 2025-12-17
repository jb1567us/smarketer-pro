<?php
// deploy_plugin_correctly.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$source_plugin = $_SERVER['DOCUMENT_ROOT'] . '/esm-artwork-template.php';
$dest_dir = WPMU_PLUGIN_DIR;
$dest_plugin = $dest_dir . '/esm-artwork-template.php';
$json_source = $_SERVER['DOCUMENT_ROOT'] . '/artwork_data.json';

echo "<h1>Plugin Deployment Check</h1>";

// 1. Ensure MU Plugins Dir exists
if (!file_exists($dest_dir)) {
    mkdir($dest_dir, 0755, true);
    echo "Created MU Plugin Dir: $dest_dir<br>";
} else {
    echo "MU Plugin Dir exists: $dest_dir<br>";
}

echo "Current Dir: " . __DIR__ . "<br>";
echo "Doc Root: " . $_SERVER['DOCUMENT_ROOT'] . "<br>";

$files = scandir(__DIR__);
echo "<h2>Files in Current Dir:</h2><ul>";
foreach ($files as $f) {
    if (strpos($f, '.php') !== false || strpos($f, '.json') !== false) {
        echo "<li>$f</li>";
    }
}
echo "</ul>";

// Check MU Plugins specifically
$mu = WPMU_PLUGIN_DIR;
echo "<h2>Files in MU Plugins ($mu):</h2><ul>";
if (is_dir($mu)) {
    $mu_files = scandir($mu);
    foreach ($mu_files as $f)
        echo "<li>$f</li>";
} else {
    echo "<li>MU Dir does not exist.</li>";
}
echo "</ul>";

// 3. Confirm JSON
if (file_exists($json_source)) {
    echo "✅ artwork_data.json found in root.<br>";
} else {
    echo "❌ artwork_data.json MISSING from root.<br>";
}

// 4. Test Shortcode Existence
if (shortcode_exists('esm_artwork_layout')) {
    echo "<h2>🎉 SUCCESS: Shortcode [esm_artwork_layout] is REGISTERED!</h2>";
} else {
    echo "<h2>⚠️ ALERT: Shortcode [esm_artwork_layout] is NOT registered yet.</h2>";
    echo "Verify file permissions and structure.";
}
?>