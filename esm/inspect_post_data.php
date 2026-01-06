<?php
// inspect_post_data.php
require_once('wp-load.php');

$title = 'Waves'; // Target problematic post
$page = get_page_by_title($title, OBJECT, 'page');

if (!$page) {
    // Try finding by slug or broad search if title match fails
    $args = [
        'post_type' => 'any',
        'title' => $title,
        'posts_per_page' => 1
    ];
    $q = new WP_Query($args);
    if ($q->have_posts()) {
        $page = $q->posts[0];
    }
}

if ($page) {
    echo "ID: " . $page->ID . "\n";
    echo "Title: " . $page->post_title . "\n";
    echo "Content Sample (first 500 chars):\n" . substr($page->post_content, 0, 500) . "\n...\n";
    
    // Check if broken link is in content
    if (strpos($page->post_content, 'saatchiart.com') !== false) {
        echo "FOUND Saatchi link in post_content!\n";
        // Extract it
        preg_match_all('/href=["\'](https?:\/\/.*?saatchiart\.com.*?)["\']/', $page->post_content, $matches);
        print_r($matches[1]);
    } else {
        echo "Saatchi link NOT found in post_content.\n";
    }

    echo "\n--- META KEYS ---\n";
    $meta = get_post_meta($page->ID);
    foreach ($meta as $k => $v) {
        // Hide some noise
        if (strpos($k, '_') === 0 && $k !== '_saatchi_url') continue; 
        echo "[$k]: " . print_r($v, true) . "\n";
    }
} else {
    echo "Post '$title' not found.\n";
}
?>
