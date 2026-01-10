<?php
// activate_plugin_v2.php
header('Content-Type: text/plain');
ini_set('display_errors', 1);

if (file_exists('wp-load.php')) {
    require_once('wp-load.php');
} elseif (file_exists('index_wp.php')) {
    require_once('wp-load.php'); 
} else {
    die("Could not find wp-load.php");
}

require_once(ABSPATH . 'wp-admin/includes/plugin.php');

echo "Flushing Cache...\n";
wp_cache_flush();

$plugin = 'esm-deployment-fix.php';
echo "Deactivating $plugin...\n";
deactivate_plugins($plugin);

echo "Activating $plugin...\n";
$result = activate_plugin($plugin);

if (is_wp_error($result)) {
    echo "Error: " . $result->get_error_message() . "\n";
} else {
    echo "SUCCESS: Plugin activated.\n";
}

// Check if class exists now
$exists = class_exists('ESM_Artwork_Template_Fix') ? 'YES' : 'NO';
echo "Class ESM_Artwork_Template_Fix exists: $exists\n";

// Check active plugins
echo "Active Plugins:\n";
print_r(get_option('active_plugins'));
?>
