<?php
// kill_plugins_debug.php
// Disable plugins to isolate theme crash

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$active_plugins = WP_CONTENT_DIR . '/plugins';
$disabled_plugins = WP_CONTENT_DIR . '/plugins.disabled_debug';

if (is_dir($active_plugins)) {
    rename($active_plugins, $disabled_plugins);
    echo "<h1>✅ Plugins Disabled (Renamed)</h1>";
} elseif (is_dir($disabled_plugins)) {
    echo "<h1>⚠️ Plugins Already Disabled</h1>";
} else {
    echo "<h1>❌ Plugins Dir Not Found</h1>";
}

echo "view site: <a href='/anemones/'>/anemones/</a>";
?>