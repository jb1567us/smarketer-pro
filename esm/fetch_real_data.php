<?php
// fetch_real_data.php
// Get the REAL Anemones data for the static file

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$id = 213;
$post = get_post($id);

echo "<h1>🎨 Real Data Extraction</h1>";

if ($post) {
    // 1. Title
    echo "<b>Title:</b> " . $post->post_title . "<br>";

    // 2. Content (Description/Meta)
    echo "<b>Content:</b> " . htmlspecialchars($post->post_content) . "<br>";

    // 3. Featured Image
    $img_id = get_post_thumbnail_id($id);
    $img_url = wp_get_attachment_url($img_id);
    echo "<b>Image URL:</b> " . ($img_url ? $img_url : "❌ No Featured Image") . "<br>";

    // 4. Custom Fields (if any, usually dimensions provided in content for this site)
    // Based on previous knowledge, dimensions/price are in the content HTML.

    // 5. Generate JSON for easy parsing
    $data = [
        'title' => $post->post_title,
        'content' => $post->post_content,
        'image' => $img_url
    ];
    echo "<hr><pre>" . json_encode($data, JSON_PRETTY_PRINT) . "</pre>";
} else {
    echo "❌ Post 213 Not Found";
}
?>