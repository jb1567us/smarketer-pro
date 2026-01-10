<?php
// check_route_collision.php
// Debug what WP thinks /anemones/ is

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$slug = 'anemones';
echo "<h1>🕵️ Route Inspector: /$slug/</h1>";

// 1. Check Collision
$page = get_page_by_path($slug);
$term = get_term_by('slug', $slug, 'category');
$tag = get_term_by('slug', $slug, 'post_tag');

if ($page)
    echo "✅ Page Found: ID {$page->ID} ({$page->post_status})<br>";
if ($term)
    echo "⚠️ Category Collision: ID {$term->term_id}<br>";
if ($tag)
    echo "⚠️ Tag Collision: ID {$tag->term_id}<br>";

// 2. Check DB Content
if ($page) {
    echo "<h3>Page Content Preview:</h3>";
    echo "<textarea style='width:100%;height:150px;'>" . htmlspecialchars(substr($page->post_content, 0, 1000)) . "</textarea>";
}

// 3. Simulate Query
global $wp_query;
$wp_query = new WP_Query(['pagename' => $slug]);
echo "<h3>Main Query Simulation:</h3>";
echo "Found Posts: " . $wp_query->found_posts . "<br>";
echo "Is Page: " . ($wp_query->is_page ? 'Yes' : 'No') . "<br>";
echo "Is Archive: " . ($wp_query->is_archive ? 'Yes' : 'No') . "<br>";

echo "<br><a href='/anemones/'>Check Site</a>";
?>