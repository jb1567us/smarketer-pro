<?php
// restore_plugins.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
$dir = WP_CONTENT_DIR . '/plugins';
$bak = WP_CONTENT_DIR . '/plugins_disabled';

if (file_exists($bak)) {
    if (rename($bak, $dir)) {
        echo "✅ Restored plugins folder.";
    } else {
        echo "❌ Failed to restore plugins folder.";
    }
} else {
    echo "⚠️ plugins_disabled not found (Already restored?).";
}
?>