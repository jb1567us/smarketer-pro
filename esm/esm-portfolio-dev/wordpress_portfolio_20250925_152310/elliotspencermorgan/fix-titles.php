<?php
require_once('wp-load.php');

// Get all posts
$posts = get_posts(array(
    'numberposts' => -1,
    'post_type' => 'post',
    'post_status' => 'publish'
));

foreach ($posts as $post) {
    $original_title = $post->post_title;
    $new_title = $original_title;
    
    // List of words to add spaces before
    $words = array('painting', 'sculpture', 'installation', 'collage');
    
    foreach ($words as $word) {
        // Simple string replacement
        $new_title = str_ireplace($word, " " . $word, $new_title);
    }
    
    // Clean up any double spaces and trim
    $new_title = preg_replace('/\s+/', ' ', $new_title);
    $new_title = trim($new_title);
    
    // Update if changed
    if ($new_title !== $original_title) {
        wp_update_post(array(
            'ID' => $post->ID,
            'post_title' => $new_title
        ));
        echo "Updated: '$original_title' to '$new_title'<br>";
    }
}

echo "Done!";
?>