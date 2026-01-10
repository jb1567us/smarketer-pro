<?php
// kill_plugins.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
$dir = WP_CONTENT_DIR . '/plugins';
$bak = WP_CONTENT_DIR . '/plugins_disabled';

if (file_exists($dir)) {
    if (rename($dir, $bak)) {
        echo "✅ Renamed plugins to plugins_disabled. ALL PLUGINS OFF.";
    } else {
        echo "❌ Failed to rename plugins folder.";
    }
} elseif (file_exists($bak)) {
    echo "⚠️ plugins_disabled already exists (Plugins already off?).";
} else {
    echo "❌ plugins folder not found.";
}
?>