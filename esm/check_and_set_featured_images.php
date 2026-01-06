<?php
// check_and_set_featured_images.php
// Find images and set them as featured images for posts

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

echo "<h1>🖼️ Setting Featured Images</h1>";

// Get all posts
$posts = get_posts([
    'post_type' => 'post',
    'posts_per_page' => -1,
    'post_status' => 'publish',
    'orderby' => 'title',
    'order' => 'ASC'
]);

echo "Found " . count($posts) . " total posts<br><br>";

$fixed = 0;
$already_have = 0;
$no_image_found = 0;

foreach ($posts as $post) {
    // Check if already has featured image
    if (get_post_thumbnail_id($post->ID)) {
        $already_have++;
        continue;
    }

    // Try to find an image in post content
    preg_match('/<img[^>]+src="([^">]+)"/', $post->post_content, $matches);

    if (!empty($matches[1])) {
        $image_url = $matches[1];

        // Get attachment ID from URL
        $attachment_id = attachment_url_to_postid($image_url);

        if ($attachment_id) {
            set_post_thumbnail($post->ID, $attachment_id);
            echo "✅ Set featured image for: {$post->post_title}<br>";
            $fixed++;
        } else {
            echo "⚠️ Found image but couldn't get attachment ID for: {$post->post_title}<br>";
            $no_image_found++;
        }
    } else {
        echo "❌ No image found in content for: {$post->post_title}<br>";
        $no_image_found++;
    }
}

echo "<br><hr>";
echo "<strong>Summary:</strong><br>";
echo "Already had featured images: $already_have<br>";
echo "Fixed (set new featured images): $fixed<br>";
echo "No image found: $no_image_found<br>";

if ($fixed > 0) {
    echo "<br><a href='/build_static_portfolio.php'>Rebuild Portfolio Now</a>";
}
?>