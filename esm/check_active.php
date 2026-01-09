<?php
// check_active.php
require_once('wp-load.php');
header('Content-Type: text/plain');

echo "Plugins Check:\n";
$plugins = get_option('active_plugins');
foreach ($plugins as $p) {
    if (strpos($p, 'esm-') !== false) {
        echo "ACTIVE: $p\n";
    }
}

echo "\nTemplate Check for Anemones:\n";
$post = get_page_by_path('anemones', OBJECT, 'post');
if (!$post) $post = get_page_by_path('anemones', OBJECT, 'page');

if ($post) {
    echo "Post Found: " . $post->post_title . " (ID: " . $post->ID . ")\n";
} else {
    echo "Post 'anemones' not found by slug.\n";
}
?>
