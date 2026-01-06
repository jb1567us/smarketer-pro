<?php
// restore_homepage_portfolio.php
// Remove placeholder content, show clean portfolio grid

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
echo "<h1>🎨 Restoring Homepage Portfolio</h1>";

// Get the home template
$home_template = get_posts([
    'post_type' => 'wp_template',
    'name' => 'home',
    'post_status' => 'any',
    'numberposts' => 1
]);

if (empty($home_template)) {
    echo "⚠️ Home template not found in DB. Will create one.<br>";

    // Create a new home template
    $template_content = <<<HTML
<!-- wp:template-part {"slug":"header","tagName":"header"} /-->

<!-- wp:group {"tagName":"main","style":{"spacing":{"margin":{"top":"var:preset|spacing|50"}}},"layout":{"type":"constrained"}} -->
<main class="wp-block-group" style="margin-top:var(--wp--preset--spacing--50)">

<!-- wp:query {"queryId":1,"query":{"perPage":100,"pages":0,"offset":0,"postType":"post","order":"desc","orderBy":"date","author":"","search":"","exclude":[],"sticky":"","inherit":false}} -->
<div class="wp-block-query">
    
    <!-- wp:query-pagination {"layout":{"type":"flex","justifyContent":"center"}} /-->

    <!-- wp:post-template {"style":{"spacing":{"blockGap":"var:preset|spacing|50"}},"layout":{"type":"grid","columnCount":3}} -->
        <!-- wp:post-featured-image {"isLink":true,"aspectRatio":"1","style":{"spacing":{"margin":{"bottom":"var:preset|spacing|20"}}}} /-->
        <!-- wp:post-title {"isLink":true,"style":{"spacing":{"margin":{"top":"0"}}}} /-->
        <!-- wp:post-excerpt {"moreText":"View Artwork","excerptLength":20} /-->
    <!-- /wp:post-template -->

    <!-- wp:query-no-results -->
        <!-- wp:paragraph {"placeholder":"Add text here"} -->
        <p>No artwork found.</p>
        <!-- /wp:paragraph -->
    <!-- /wp:query-no-results -->

</div>
<!-- /wp:query -->

</main>
<!-- /wp:group -->

<!-- wp:template-part {"slug":"footer","tagName":"footer"} /-->
HTML;

    $new_template = wp_insert_post([
        'post_type' => 'wp_template',
        'post_name' => 'home',
        'post_title' => 'Home',
        'post_content' => $template_content,
        'post_status' => 'publish',
        'tax_input' => [
            'wp_theme' => ['twentytwentyfour']
        ]
    ]);

    if ($new_template) {
        echo "✅ Created new Home template: ID $new_template<br>";
    } else {
        echo "❌ Failed to create home template<br>";
    }

} else {
    // Update existing home template
    $template = $home_template[0];

    $template_content = <<<HTML
<!-- wp:template-part {"slug":"header","tagName":"header"} /-->

<!-- wp:group {"tagName":"main","style":{"spacing":{"margin":{"top":"var:preset|spacing|50"}}},"layout":{"type":"constrained"}} -->
<main class="wp-block-group" style="margin-top:var(--wp--preset--spacing--50)">

<!-- wp:query {"queryId":1,"query":{"perPage":100,"pages":0,"offset":0,"postType":"post","order":"desc","orderBy":"date","author":"","search":"","exclude":[],"sticky":"","inherit":false}} -->
<div class="wp-block-query">
    
    <!-- wp:query-pagination {"layout":{"type":"flex","justifyContent":"center"}} /-->

    <!-- wp:post-template {"style":{"spacing":{"blockGap":"var:preset|spacing|50"}},"layout":{"type":"grid","columnCount":3}} -->
        <!-- wp:post-featured-image {"isLink":true,"aspectRatio":"1","style":{"spacing":{"margin":{"bottom":"var:preset|spacing|20"}}}} /-->
        <!-- wp:post-title {"isLink":true,"style":{"spacing":{"margin":{"top":"0"}}}} /-->
        <!-- wp:post-excerpt {"moreText":"View Artwork","excerptLength":20} /-->
    <!-- /wp:post-template -->

    <!-- wp:query-no-results -->
        <!-- wp:paragraph {"placeholder":"Add text here"} -->
        <p>No artwork found.</p>
        <!-- /wp:paragraph -->
    <!-- /wp:query-no-results -->

</div>
<!-- /wp:query -->

</main>
<!-- /wp:group -->

<!-- wp:template-part {"slug":"footer","tagName":"footer"} /-->
HTML;

    wp_update_post([
        'ID' => $template->ID,
        'post_content' => $template_content
    ]);

    echo "✅ Updated Home template (ID: {$template->ID})<br>";
}

if (function_exists('opcache_reset'))
    opcache_reset();
if (function_exists('wp_cache_flush'))
    wp_cache_flush();

echo "<br><a href='/'>Check Homepage</a>";
?>