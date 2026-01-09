
<?php
// activate_plugin.php
require_once('wp-load.php');
include_once( ABSPATH . 'wp-admin/includes/plugin.php' );

echo "<pre>Activating ESM Trade Portal...\n";

$plugin = 'esm-trade-portal/esm-trade-portal.php';

// Check if already active
if (is_plugin_active($plugin)) {
    echo "Plugin is ALREADY ACTIVE.\n";
} else {
    $result = activate_plugin($plugin);
    if (is_wp_error($result)) {
        echo "ERROR: " . $result->get_error_message() . "\n";
    } else {
        echo "SUCCESS: Plugin activated.\n";
    }
}

// Flush Rules
global $wp_rewrite;
$wp_rewrite->flush_rules();
echo "Rewrite rules flushed.\n";

echo "Check: <a href='/trade/'>/trade/</a>\n";
echo "</pre>";
?>
