<?php
// deploy_trade.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$source = ABSPATH . 'esm-trade-portal.php';
$dest = WPMU_PLUGIN_DIR . '/esm-trade-portal.php';

echo "<h1>Trade Portal Deployment</h1>";

if (file_exists($source)) {
    echo "✅ Source found.<br>";
    if (!is_dir(WPMU_PLUGIN_DIR))
        mkdir(WPMU_PLUGIN_DIR, 0755, true);

    // Copy
    if (copy($source, $dest)) {
        echo "✅ INSTALLED to $dest<br>";
        unlink($source);

        // FLUSH RULES
        flush_rewrite_rules();
        echo "✅ Rewrite Rules Flushed.<br>";
    } else {
        echo "❌ Copy failed.<br>";
    }
} else {
    echo "❌ Source missing.<br>";
}

echo "<br><a href='/trade/' target='_blank'>OPEN PORTAL >></a>";
?>