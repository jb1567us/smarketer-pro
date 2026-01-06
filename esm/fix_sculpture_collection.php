<?php
// Fix Sculpture Collection Page - Remove "Floating Leaves"
// Run with: wp eval-file fix_sculpture_collection.php
// Or place in root and visit (but we assume CLI usage here)

require_once('wp-load.php');

$page_slug = 'sculpture-collection';
$target_title = 'Floating Leaves';

echo "Searching for page with slug: $page_slug\n";

$args = array(
    'name'        => $page_slug,
    'post_type'   => 'page',
    'post_status' => 'publish',
    'numberposts' => 1
);

$query = new WP_Query($args);

if ($query->have_posts()) {
    $query->the_post(); // logic setup
    $post_id = get_the_ID();
    $content = get_post_field('post_content', $post_id);
    
    echo "Found page ID: $post_id\n";
    echo "Content length: " . strlen($content) . " bytes\n";
    
    // Check if target exists
    if (strpos($content, $target_title) === false) {
        echo "TARGET NOT FOUND: '$target_title' is not in the page content.\n";
        echo "It might be generated dynamically or already removed.\n";
        exit;
    }
    
    echo "Target '$target_title' FOUND in content.\n";
    
    // Regex to remove the card
    // Structure:
    // <div class="artwork-card" ...>
    //    ...
    //    <h3 ...>...Floating Leaves...</h3>
    //    ...
    // </div>
    
    // Pattern: Match <div class="artwork-card"> ... Floating Leaves ... </div>
    // We rely on non-greedy match to find the closing div of the SAME card.
    // Since there are no nested divs in the card (verified in source), this is safe.
    $pattern = '/<div class="artwork-card"[^>]*>[\s\S]*?Floating Leaves[\s\S]*?<\/div>/i';
    
    $new_content = preg_replace($pattern, '', $content, 1, $count);
    
    if ($count > 0) {
        echo "Removed $count instance(s) of the artwork card.\n";
        
        // Update the post
        $updated_post = array(
            'ID'           => $post_id,
            'post_content' => $new_content
        );
        
        $result = wp_update_post($updated_post);
        
        if (is_wp_error($result)) {
            echo "ERROR updating post: " . $result->get_error_message() . "\n";
        } else {
            echo "SUCCESS: Page updated. content length is now " . strlen($new_content) . " bytes.\n";
        }
        
    } else {
        echo "REGEX FAILED to match content despite strpos finding it.\n";
        // Dump snippet for debugging
        $pos = strpos($content, $target_title);
        $snippet = substr($content, max(0, $pos - 200), 400);
        echo "Snippet context:\n$snippet\n";
    }
    
} else {
    echo "Page not found.\n";
}

echo "Done.\n";
