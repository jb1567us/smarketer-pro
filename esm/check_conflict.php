
<?php
error_reporting(E_ALL);
ini_set('display_errors', 1);

echo "<pre>Checking for Page Conflicts...\n";

if (file_exists('wp-load.php')) {
    require_once('wp-load.php');
} else {
    die("wp-load.php not found.");
}

$slug = 'trade';
$page = get_page_by_path($slug);

if ($page) {
    echo "CONFLICT DETECTED: Page '$slug' exists (ID: {$page->ID}).\n";
    echo "Status: " . $page->post_status . "\n";
    
    // Auto-Trash the conflicting page to allow Plugin to take over
    echo "Attempting to trash conflicting page...\n";
    $update = wp_update_post([
        'ID' => $page->ID,
        'post_status' => 'trash'
    ]);
    
    if (is_wp_error($update)) {
        echo "Error trashing page: " . $update->get_error_message() . "\n";
    } else {
        echo "SUCCESS: Page trashed. Plugin should now handle /trade/.\n";
    }
} else {
    echo "No page with slug '$slug' found. Good.\n";
}

// Flush Rules
global $wp_rewrite;
$wp_rewrite->flush_rules();
echo "Rewrite Rules Flushed.\n";

echo "</pre>";
?>
