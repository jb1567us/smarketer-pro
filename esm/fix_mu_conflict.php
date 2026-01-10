
<?php
// fix_mu_conflict.php
echo "<pre>Fixing MU Plugin Conflict...\n";

// 1. Delete MU Plugins
$mu_files = [
    'wp-content/mu-plugins/esm-trade-portal.php',
    'wp-content/mu-plugins/esm-trade-portal.js',
    'content/mu-plugins/esm-trade-portal.php', // Check alternate path too
    'content/mu-plugins/esm-trade-portal.js'
];

foreach ($mu_files as $file) {
    if (file_exists($file)) {
        if (unlink($file)) {
            echo "SUCCESS: Deleted conflicting MU file: $file\n";
        } else {
            echo "ERROR: Failed to delete: $file\n";
        }
    } else {
        echo "Not found: $file\n";
    }
}

// 2. Activate Regular Plugin
require_once('wp-load.php');
include_once( ABSPATH . 'wp-admin/includes/plugin.php' );

$plugin = 'esm-trade-portal/esm-trade-portal.php';
$result = activate_plugin($plugin);

if (is_wp_error($result)) {
    echo "Error activating regular plugin: " . $result->get_error_message() . "\n";
} else {
    echo "SUCCESS: Activated regular plugin '$plugin'.\n";
}

// 3. Flush Rules again to be safe
global $wp_rewrite;
$wp_rewrite->flush_rules();
echo "Rewrite rules flushed.\n";

echo "DONE.</pre>";
?>
