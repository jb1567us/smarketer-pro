<?php
// fix_homepage_front_page.php
// Set "Posts page" as front page AND update the index template

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
echo "<h1>🏠 Fixing Homepage Settings</h1>";

// Check current settings
$show_on_front = get_option('show_on_front');
$page_on_front = get_option('page_on_front');
$page_for_posts = get_option('page_for_posts');

echo "Current Settings:<br>";
echo "- show_on_front: $show_on_front<br>";
echo "- page_on_front: $page_on_front<br>";
echo "- page_for_posts: $page_for_posts<br><br>";

// Set to show posts on front page
update_option('show_on_front', 'posts');
update_option('page_on_front', 0);
echo "✅ Set homepage to show posts<br>";

// Now update the INDEX template (used when show_on_front is 'posts')
$index_template = get_posts([
    'post_type' => 'wp_template',
    'name' => 'index',
    'post_status' => 'any',
    'numberposts' => 1
]);

$template_content = <<<HTML
<!-- wp:template-part {"slug":"header","tagName":"header"} /-->

<!-- wp:group {"tagName":"main","style":{"spacing":{"margin":{"top":"var:preset|spacing|50"}}},"layout":{"type":"constrained"}} -->
<main class="wp-block-group" style="margin-top:var(--wp--preset--spacing--50)">

<!-- wp:query {"queryId":1,"query":{"perPage":100,"pages":0,"offset":0,"postType":"post","order":"desc","orderBy":"date","author":"","search":"","exclude":[],"sticky":"","inherit":false}} -->
<div class="wp-block-query">
    
    <!-- wp:post-template {"style":{"spacing":{"blockGap":"var:preset|spacing|50"}},"layout":{"type":"grid","columnCount":3}} -->
        <!-- wp:post-featured-image {"isLink":true,"aspectRatio":"1","style":{"spacing":{"margin":{"bottom":"var:preset|spacing|20"}}}} /-->
        <!-- wp:post-title {"isLink":true,"style":{"spacing":{"margin":{"top":"0"}}}} /-->
        <!-- wp:post-excerpt {"moreText":"View Artwork","excerptLength":20} /-->
    <!-- /wp:post-template -->

    <!-- wp:query-pagination {"layout":{"type":"flex","justifyContent":"center"}} /-->

    <!-- wp:query-no-results -->
        <!-- wp:paragraph -->
        <p>No artwork found.</p>
        <!-- /wp:paragraph -->
    <!-- /wp:query-no-results -->

</div>
<!-- /wp:query -->

</main>
<!-- /wp:group -->

<!-- wp:template-part {"slug":"footer","tagName":"footer"} /-->
HTML;

if (!empty($index_template)) {
    $template = $index_template[0];
    wp_update_post([
        'ID' => $template->ID,
        'post_content' => $template_content
    ]);
    echo "✅ Updated Index template (ID: {$template->ID})<br>";
} else {
    echo "⚠️ Index template not found<br>";
}

if (function_exists('opcache_reset'))
    opcache_reset();
if (function_exists('wp_cache_flush'))
    wp_cache_flush();

echo "<br><a href='/'>Check Homepage Now</a>";
?>