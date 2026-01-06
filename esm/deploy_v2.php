<?php
// deploy_v2.php
// Moves esm-template-v2.php from Root -> MU-Plugins/esm-artwork-template.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$source = ABSPATH . 'esm-template-v2.php';
$dest = WPMU_PLUGIN_DIR . '/esm-artwork-template.php';

echo "<h1>Deployment V2</h1>";

if (file_exists($source)) {
    echo "✅ Found uploaded source: $source<br>";

    // Ensure dest dir
    if (!is_dir(WPMU_PLUGIN_DIR))
        mkdir(WPMU_PLUGIN_DIR, 0755, true);

    // Force Move
    if (copy($source, $dest)) {
        echo "✅ COPIED to $dest<br>";
        unlink($source);
        echo "✅ Deleted source.<br>";
    } else {
        echo "❌ FAILED to copy.<br>";
    }
} else {
    echo "❌ Source NOT found: $source<br>";
}

// Verification
if (shortcode_exists('esm_artwork_layout')) {
    echo "<h2>🎉 Shortcode ACTIVE!</h2>";
} else {
    echo "<h2>⚠️ Shortcode NOT Detected yet (might need refresh)</h2>";
}
?>