<?php
require_once('wp-load.php');

$titles = [
    'City at Night Mulch Series',
    'Close up Mulch Series',
    'Red and Black Mulch Series',
    'Megapixels',
    'Existance', 
    'Existence' // Checking correct spelling too
];

foreach ($titles as $title) {
    $page = get_page_by_title($title, OBJECT, 'page');
    if ($page) {
        $thumb_id = get_post_thumbnail_id($page->ID);
        $img_url = wp_get_attachment_url($thumb_id);
        echo "Found: '{$title}' (ID: {$page->ID})\n";
        echo "  Featured Image: " . ($img_url ? $img_url : "None") . "\n";
    } else {
        // Try fuzzy search
        $args = array(
            'post_type' => 'page',
            's' => $title,
            'posts_per_page' => 1
        );
        $query = new WP_Query($args);
        if ($query->have_posts()) {
            $query->the_post();
            $thumb_id = get_post_thumbnail_id(get_the_ID());
            $img_url = wp_get_attachment_url($thumb_id);
            echo "Found (fuzzy): '" . get_the_title() . "' matched '{$title}'\n";
            echo "  Featured Image: " . ($img_url ? $img_url : "None") . "\n";
            wp_reset_postdata();
        } else {
            echo "Not Found: '{$title}'\n";
        }
    }
}
