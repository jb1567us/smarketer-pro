<?php
// cleanup_pages.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$titles_to_remove = [
    "A Day at the Lake",
    "A day at the park",
    "A day at the beach",
    "Abstract Landscape",
    "Portal 001 Painting",
    "Portal 002 Painting",
    "Portal 003 Painting",
    "Portal 004 Painting",
    "Portal 005 Painting",
    "Portal 006 Painting",
    "Portal 1 Painting",
    "Gold Series 007",
    "Gold Series 008",
    "Gold Series 009",
    "Gold Series 010",
    "Gold Series 011",
    "Puzzle",
    "Red and Black - Mulch Series Collage",
    "Pieces of Red",
    "City at Night - Mulch Series Collage",
    "Close up - Mulch Series Collage"
];

$deleted = 0;

foreach ($titles_to_remove as $title) {
    $page = get_page_by_title($title, OBJECT, 'page');
    if ($page) {
        // Double check it's one of ours?
        wp_delete_post($page->ID, true); // Force delete
        echo "✅ Deleted Page: $title (ID: {$page->ID})<br>";
        $deleted++;
    } else {
        // Try slug?
        $slug = sanitize_title($title);
        $args = ['name' => $slug, 'post_type' => 'page', 'numberposts' => 1];
        $posts = get_posts($args);
        if ($posts) {
            wp_delete_post($posts[0]->ID, true);
            echo "✅ Deleted Page (by slug): $title (Slot: $slug)<br>";
            $deleted++;
        } else {
            echo "⚠️ Not Found: $title<br>";
        }
    }
}

echo "Done. Deleted $deleted pages.";
?>