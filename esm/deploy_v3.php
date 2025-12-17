<?php
// deploy_v3.php
// Moves esm-template-v3.php from Root -> MU-Plugins/esm-artwork-template.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$source = ABSPATH . 'esm-template-v3.php';
$dest = WPMU_PLUGIN_DIR . '/esm-artwork-template.php';

echo "<h1>Deployment V3</h1>";

if (file_exists($source)) {
    echo "✅ Found source: $source<br>";
    if (!is_dir(WPMU_PLUGIN_DIR))
        mkdir(WPMU_PLUGIN_DIR, 0755, true);

    if (copy($source, $dest)) {
        echo "✅ INSTALLED v3 to $dest<br>";
        unlink($source);
        echo "✅ Cleanup complete.<br>";
    } else {
        echo "❌ OVERWRITE FAILED (Permission likely). Attempting rename-swap...<br>";
        // Rename swap
        $backup = $dest . '.bak';
        rename($dest, $backup);
        if (copy($source, $dest)) {
            echo "✅ SWAP Success!<br>";
            unlink($source);
        } else {
            echo "❌ SWAP Failed. Backup at $backup<br>";
        }
    }
} else {
    echo "❌ Source missing: $source<br>";
}

// Verification
if (shortcode_exists('esm_artwork_layout')) {
    echo "<h2>🎉 Shortcode ACTIVE!</h2>";
}
?>