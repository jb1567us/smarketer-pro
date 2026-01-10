
<?php
// check_rewrite.php
require_once('wp-load.php');

echo "<pre>";
echo "Checking WordPress State...\n";

// 1. Check Plugin Active
include_once( ABSPATH . 'wp-admin/includes/plugin.php' );
if ( is_plugin_active( 'esm-trade-portal/esm-trade-portal.php' ) ) {
    echo "Plugin 'esm-trade-portal' is ACTIVE.\n";
} else {
    echo "Plugin 'esm-trade-portal' is INACTIVE.\n";
    // Try to activate
    activate_plugin( 'esm-trade-portal/esm-trade-portal.php' );
    echo "Attempted activation.\n";
}

// 2. Check for Page Conflict
$page = get_page_by_path('trade');
if ($page) {
    echo "WARNING: A WordPress Page with slug 'trade' EXISTS (ID: {$page->ID}).\n";
    echo "This page will likely override the plugin's virtual page.\n";
    echo "Page Status: " . $page->post_status . "\n";
} else {
    echo "No conflicting Page found for 'trade'.\n";
}

// 3. Flush Rules
echo "Flushing Rewrite Rules...\n";
global $wp_rewrite;
$wp_rewrite->flush_rules();
echo "Rewrite rules flushed.\n";

// 4. List Top Rules to verify
echo "Top Rewrite Rules:\n";
$rules = $wp_rewrite->wp_rewrite_rules();
$head = array_slice($rules, 0, 5);
print_r($head);

echo "</pre>";
?>
