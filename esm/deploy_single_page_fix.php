<?php
// deploy_single_page_fix.php
// Purpose: Update the 'Caviar' page to use the [esm_artwork_layout] shortcode.

// 1. Bootstrap WordPress
// Adjust path if needed, typical structure is usually relative to where this file is dropped.
// Assuming this file is in c:\sandbox\esm\, and wp-load is usually in the root or accessible.
// Since we are in a sandbox list of files, I'll try to find wp-load.
// Based on deploy_caviar.php line 97: require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
// I will use a more robust search or assume standard path.
// But wait, the user is running this locally or on a server? 
// The environment seems to be a sandbox mirroring a server structure. 
// I'll assume standard WP bootstrap.

require_once('wp-load.php'); // Try local if in root
if (!defined('ABSPATH')) {
    // If not found, try one level up or common paths
    if (file_exists('../wp-load.php'))
        require_once('../wp-load.php');
    elseif (file_exists('../../wp-load.php'))
        require_once('../../wp-load.php');
    else
        die("Could not find wp-load.php");
}

// 2. Define the Target
$target_slug = 'caviarpainting'; // Based on artwork_data.json id 1585, slug is 'caviarpainting'
$target_title = 'Caviar';

// 3. Find the Post
$args = [
    'name' => $target_slug,
    'post_type' => 'page',
    'post_status' => 'publish',
    'numberposts' => 1
];

$posts = get_posts($args);

// Fallback to title search if slug fails
if (!$posts) {
    $post = get_page_by_title($target_title);
    if ($post)
        $posts = [$post];
}

if (!$posts) {
    echo "❌ Could not find page with slug '$target_slug' or title '$target_title'.\n";

    // Debug: List some pages to see what exists
    echo "Listing recent pages to help debug:\n";
    $recent = get_posts(['post_type' => 'page', 'numberposts' => 5]);
    foreach ($recent as $p) {
        echo "- " . $p->post_title . " (Slug: " . $p->post_name . ")\n";
    }
    exit;
}

$post_id = $posts[0]->ID;
echo "✅ Found Post: " . $posts[0]->post_title . " (ID: $post_id)\n";

// 4. Update the Content
$new_content = '[esm_artwork_layout]';

$updated_post = [
    'ID' => $post_id,
    'post_content' => $new_content,
];

$result = wp_update_post($updated_post);

if (is_wp_error($result)) {
    echo "❌ Error updating post: " . $result->get_error_message() . "\n";
} else {
    echo "🎉 Success! Page updated to use shortcode.\n";
    echo "New Content: \n" . $new_content . "\n";
    echo "View it at: " . get_permalink($post_id) . "\n";
}
?>