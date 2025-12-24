<?php
ini_set('display_errors', 1);
error_reporting(E_ALL);
include('wp-config.php');

$files_to_delete = [
    WP_CONTENT_DIR . '/mu-plugins/esm-artwork-template_NEW.php',
    WP_CONTENT_DIR . '/plugins/esm-template-v3.php',
    // Also check for any other variations I saw earlier
    WP_CONTENT_DIR . '/mu-plugins/esm-deployment-fix.php', 
    WP_CONTENT_DIR . '/plugins/esm-artwork-template.php' // If we want to strictly use esm-deployment-fix
];

// Let's keep esm-deployment-fix.php in plugins as the winner.
// So we DELETE esm-artwork-template.php in plugins too to prevent duplicate valid plugins.

echo "<h1>Cleaning up Conflicting Plugins</h1>";

foreach ($files_to_delete as $file) {
    if (file_exists($file)) {
        if (unlink($file)) {
            echo "<p style='color:green'>Deleted: $file</p>";
        } else {
            echo "<p style='color:red'>Failed to delete: $file</p>";
        }
    } else {
        echo "<p style='color:gray'>Not found: $file</p>";
    }
}

// Verify what is left
echo "<h2>Remaining Plugins</h2>";
$plugins = glob(WP_CONTENT_DIR . '/plugins/*.php');
foreach ($plugins as $p) {
    echo basename($p) . "<br>";
}

echo "<h2>Remaining MU-Plugins</h2>";
$mu = glob(WP_CONTENT_DIR . '/mu-plugins/*.php');
if ($mu) {
    foreach ($mu as $m) {
        echo basename($m) . "<br>";
    }
} else {
    echo "No MU plugins found.<br>";
}
flush_rewrite_rules();
echo "<p>Rewrite rules flushed.</p>";
?>
