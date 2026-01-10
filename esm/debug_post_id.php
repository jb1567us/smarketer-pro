<?php
// debug_post_id.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$id = 213;
$post = get_post($id);

echo "<h1>🔍 Post ID $id</h1>";
if ($post) {
    echo "Title: " . $post->post_title . "<br>";
    echo "Slug: " . $post->post_name . "<br>";
    echo "Status: " . $post->post_status . "<br>";
    echo "Content Length: " . strlen($post->post_content) . " chars<br>";
    echo "Content Preview: " . htmlspecialchars(substr($post->post_content, 0, 100)) . "...<br>";

    // Check if category exists with same slug
    $cat = get_term_by('slug', $post->post_name, 'category');
    if ($cat)
        echo "⚠️ Category Collision with slug '{$post->post_name}'<br>";
} else {
    echo "❌ Post Not Found.";
}
?>