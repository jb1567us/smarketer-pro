<?php
require_once('wp-load.php');
$slug = 'portal-2';
$id = url_to_postid(home_url('/' . $slug));
echo "<h1>ID Check for '$slug'</h1>";
echo "Resolved ID: " . $id . "<br>";

if ($id) {
    $p = get_post($id);
    echo "Title: " . $p->post_title . "<br>";
    echo "Content Length: " . strlen($p->post_content) . "<br>";
    echo "Content Preview: " . htmlspecialchars(substr($p->post_content, 0, 100));
}

// Also check ID 1927
echo "<h2>Check ID 1927</h2>";
$p2 = get_post(1927);
if ($p2) {
    echo "Title: " . $p2->post_title . "<br>";
    echo "Content Length: " . strlen($p2->post_content) . "<br>";
    echo "Slug: " . $p2->post_name . "<br>";
} else {
    echo "ID 1927 not found";
}
?>