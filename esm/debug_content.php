<?php
require_once('wp-load.php');
$id = 1927; // Portal
$post = get_post($id);
if ($post) {
    echo "<h1>Raw Content for ID $id</h1>";
    echo "<textarea cols=100 rows=20>";
    echo htmlspecialchars($post->post_content);
    echo "</textarea>";
} else {
    echo "Post not found";
}
?>