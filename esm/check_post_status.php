<?php
// check_post_status.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
$id = 213;
$p = get_post($id);

echo "<h1>Post Status ID $id</h1>";
if ($p) {
    echo "Status: " . $p->post_status . "<br>";
    echo "Type: " . $p->post_type . "<br>";
    echo "Title: " . $p->post_title . "<br>";
    echo "Content Len: " . strlen($p->post_content) . "<br>";
    echo "Password: [" . $p->post_password . "]<br>";
} else {
    echo "Post NOT FOUND object<br>";
}

// Check Query
$q = new WP_Query(['page_id' => $id]);
echo "<h3>Custom Query Check</h3>";
echo "Found Posts: " . $q->found_posts . "<br>";
echo "Post Count: " . $q->post_count . "<br>";
if ($q->have_posts()) {
    while ($q->have_posts()) {
        $q->the_post();
        echo "Loop Title: " . get_the_title() . "<br>";
    }
} else {
    echo "Custom Query Empty.<br>";
}
?>