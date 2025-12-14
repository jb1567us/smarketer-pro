<?php
// kill_all_plugins_final.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
$dir = WP_CONTENT_DIR . '/plugins';
$bak = WP_CONTENT_DIR . '/plugins.disabled_final';

if (rename($dir, $bak)) {
    echo "✅ Plugins Disabled (Renamed to plugins.disabled_final).";
} else {
    echo "❌ Failed to disable plugins.";
}
?>