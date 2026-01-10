<?php
// force_homepage_to_posts_final.php
// Delete the static homepage page and force blog to show

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
echo "<h1>🏠 Forcing Homepage to Posts</h1>";

// Check what's set as homepage
$page_on_front = get_option('page_on_front');
if ($page_on_front) {
    $page = get_post($page_on_front);
    if ($page) {
        echo "Found static homepage: ID=$page_on_front, Title='{$page->post_title}'<br>";

        // Delete or trash it
        wp_delete_post($page_on_front, true);
        echo "✅ Deleted static homepage<br>";
    }
}

// Force settings
update_option('show_on_front', 'posts');
update_option('page_on_front', 0);
update_option('page_for_posts', 0);
echo "✅ Set homepage to show posts<br>";

// Update ALL templates that might be the homepage
global $wpdb;
$templates = $wpdb->get_results("
    SELECT ID, post_name, post_title, post_content 
    FROM {$wpdb->posts} 
    WHERE post_type = 'wp_template' 
    AND post_status != 'trash'
");

echo "<br>Found " . count($templates) . " templates total<br><br>";

$portfolio_grid = <<<HTML
<!-- wp:template-part {"slug":"header","tagName":"header"} /-->

<!-- wp:group {"tagName":"main","style":{"spacing":{"margin":{"top":"var:preset|spacing|50"}}},"layout":{"type":"constrained"}} -->
<main class="wp-block-group" style="margin-top:var(--wp--preset--spacing--50)">

<!-- wp:query {"queryId":1,"query":{"perPage":100,"pages":0,"offset":0,"postType":"post","order":"desc","orderBy":"date"}} -->
<div class="wp-block-query">
    
    <!-- wp:post-template {"style":{"spacing":{"blockGap":"var:preset|spacing|50"}},"layout":{"type":"grid","columnCount":3}} -->
        <!-- wp:post-featured-image {"isLink":true,"aspectRatio":"1"} /-->
        <!-- wp:post-title {"isLink":true} /-->
    <!-- /wp:post-template -->

</div>
<!-- /wp:query -->

</main>
<!-- /wp:group -->

<!-- wp:template-part {"slug":"footer","tagName":"footer"} /-->
HTML;

foreach ($templates as $t) {
    // Update home, index, front-page templates
    if (in_array($t->post_name, ['home', 'index', 'front-page', 'twentytwentyfour//home', 'twentytwentyfour//index'])) {
        echo "Updating: {$t->post_name} (ID: {$t->ID})<br>";

        $wpdb->update(
            $wpdb->posts,
            ['post_content' => $portfolio_grid],
            ['ID' => $t->ID]
        );
    }
}

if (function_exists('opcache_reset'))
    opcache_reset();
if (function_exists('wp_cache_flush'))
    wp_cache_flush();

echo "<br>✅ Done. <a href='/'>Check Homepage</a>";
?>