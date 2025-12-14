<?php
// delete_mu_rescue.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
$file = WPMU_PLUGIN_DIR . '/rescue.php';

if (file_exists($file)) {
    if (unlink($file)) {
        echo "✅ Deleted mu-plugins/rescue.php";
    } else {
        echo "❌ Failed to delete rescue.php";
    }
} else {
    echo "⚠️ rescue.php not found in mu-plugins";
}
?>