<?php
// generate_static_portfolio.php
// Generate a static HTML portfolio page

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
echo "<h1>Create Static Portfolio</h1>";

// Get all posts with images
$posts = get_posts([
    'post_type' => 'post',
    'posts_per_page' => -1,
    'post_status' => 'publish',
    'orderby' => 'date',
    'order' => 'DESC'
]);

echo "Found " . count($posts) . " posts<br><br>";

$portfolio_html = '';
$count = 0;

foreach ($posts as $post) {
    $thumbnail_id = get_post_thumbnail_id($post->ID);

    if ($thumbnail_id) {
        $image_url = wp_get_attachment_image_url($thumbnail_id, 'large');
        $title = get_the_title($post->ID);

        echo "✅ " . $title . " - Has image<br>";
        $count++;
    } else {
        echo "⚠️ " . $title . " - NO IMAGE<br>";
    }
}

echo "<br>Total posts with images: $count<br>";
echo "<a href='/'>Check Homepage</a>";
?>