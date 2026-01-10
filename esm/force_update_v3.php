<?php
// force_update_v3.php
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

$plugins_to_kill = [
    'wp-optimize/wp-optimize.php',
    'siteseo/siteseo.php',
    'siteseo-pro/siteseo-pro.php'
];

echo "Deactivating potential blockers:\n";
foreach ($plugins_to_kill as $p) {
    if (is_plugin_active($p)) {
        deactivate_plugins($p);
        echo " - Deactivated $p\n";
    } else {
        echo " - $p was not active\n";
    }
}

echo "Flushing Object Cache...\n";
wp_cache_flush();

$plugin = 'esm-deployment-fix.php';
// Deactivate first to force reload
deactivate_plugins($plugin);
$result = activate_plugin($plugin);

if (is_wp_error($result)) {
    echo "Error reactivating fix: " . $result->get_error_message() . "\n";
} else {
    echo "SUCCESS: Plugin activated.\n";
}

// Check if class exists now
$exists = class_exists('ESM_Artwork_Template_Fix') ? 'YES' : 'NO';
echo "Class ESM_Artwork_Template_Fix exists: $exists\n";
?>
