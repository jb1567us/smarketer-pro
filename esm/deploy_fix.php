<?php
// deploy_fix.php (Renamed from deploy_plugin_correctly.php)
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$source_plugin = $_SERVER['DOCUMENT_ROOT'] . '/esm-artwork-template.php';
$dest_dir = WPMU_PLUGIN_DIR;
$dest_plugin = $dest_dir . '/esm-artwork-template.php';

echo "<h1>Deployment Fix (Renamed)</h1>";
echo "Current Dir: " . __DIR__ . "<br>";
echo "Doc Root: " . $_SERVER['DOCUMENT_ROOT'] . "<br>";

// 1. Check Source
if (file_exists($source_plugin)) {
    echo "✅ Found source: $source_plugin<br>";

    // Ensure Destination Dir
    if (!is_dir($dest_dir)) {
        mkdir($dest_dir, 0755, true);
        echo "Created MU Dir: $dest_dir<br>";
    }

    // Move
    if (rename($source_plugin, $dest_plugin)) {
        echo "✅ MOVED plugin to: $dest_plugin<br>";
    } else {
        echo "❌ FAILED to move (permissions?). Trying copy...<br>";
        if (copy($source_plugin, $dest_plugin)) {
            echo "✅ COPIED plugin to: $dest_plugin<br>";
            unlink($source_plugin); // Cleanup
        } else {
            echo "❌ FAILED to copy.<br>";
        }
    }
} elseif (file_exists($dest_plugin)) {
    echo "✅ Plugin ALREADY exists in MU Dir: $dest_plugin<br>";
} else {
    echo "❌ Plugin NOT found in Root or MU Dir.<br>";

    // List Root Files to debug
    echo "<h3>Files in Root:</h3><ul>";
    $files = scandir($_SERVER['DOCUMENT_ROOT']);
    foreach ($files as $f) {
        if (strpos($f, 'esm') !== false)
            echo "<li>$f</li>";
    }
    echo "</ul>";
}

// 2. Check Shortcode
if (shortcode_exists('esm_artwork_layout')) {
    echo "<h2>🎉 SUCCESS: Shortcode [esm_artwork_layout] Active!</h2>";
} else {
    echo "<h2>⚠️ Shortcode NOT Registered</h2>";
}
?>