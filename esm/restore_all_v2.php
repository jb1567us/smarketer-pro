<?php
// restore_all_v2.php
// RESTORE THEME AND PLUGINS

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

// 1. Restore functions.php
$themeDir = WP_CONTENT_DIR . '/themes/esm-portfolio';
if (file_exists($themeDir . '/functions.php.bak2')) {
    rename($themeDir . '/functions.php.bak2', $themeDir . '/functions.php');
    echo "✅ Restored functions.php<br>";
} else {
    echo "⚠️ functions.php.bak2 not found (likely already restored)<br>";
}

// 2. Switch Theme
update_option('template', 'esm-portfolio');
update_option('stylesheet', 'esm-portfolio');
echo "✅ Active Theme Set to: " . get_option('stylesheet') . "<br>";

// 3. Restore Plugins
$pluginDir = WP_CONTENT_DIR . '/plugins';
$pluginBak = WP_CONTENT_DIR . '/plugins.disabled_final';

if (is_dir($pluginBak)) {
    if (file_exists($pluginDir)) {
        // safety check if plugins folder was recreated by WP
        rename($pluginDir, $pluginDir . '_temp_' . time());
    }
    rename($pluginBak, $pluginDir);
    echo "✅ Restored plugins folder.<br>";
} else {
    echo "⚠️ plugins.disabled_final not found (likely already restored)<br>";
}

echo "<h1>FULL RESTORATION COMPLETE</h1>";
?>