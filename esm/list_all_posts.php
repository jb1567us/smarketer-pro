<?php
// list_all_posts.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

echo "<textarea style='width:100%;height:500px;'>";
echo "START_LIST\n";

$args = [
    'post_type' => 'page',
    'posts_per_page' => 20,
    'post_status' => 'any',
];

$q = new WP_Query($args);
if ($q->have_posts()) {
    while ($q->have_posts()) {
        $q->the_post();
        echo "ID: " . get_the_ID() . " | Title: " . get_the_title() . " | Status: " . get_post_status() . "\n";
    }
} else {
    echo "NO POSTS FOUND.\n";
}
echo "END_LIST";
echo "</textarea>";
?>