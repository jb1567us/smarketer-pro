<?php
// update_home_template_directly.php
// Directly update the Home template with artwork grid

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
echo "<h1>🎨 Updating Home Template Directly</h1>";

// Find and update the HOME template (not index)
$home_templates = get_posts([
    'post_type' => 'wp_template',
    'post_status' => 'any',
    'numberposts' => -1
]);

echo "Found " . count($home_templates) . " total templates<br>";

foreach ($home_templates as $template) {
    if (
        strpos($template->post_name, 'home') !== false ||
        strpos($template->post_title, 'Home') !== false
    ) {
        echo "Found Home template: ID={$template->ID}, Name={$template->post_name}, Title={$template->post_title}<br>";

        // Update with artwork grid
        $template_content = <<<HTML
<!-- wp:template-part {"slug":"header","tagName":"header"} /-->

<!-- wp:group {"tagName":"main","style":{"spacing":{"margin":{"top":"var:preset|spacing|50"}}},"layout":{"type":"constrained"}} -->
<main class="wp-block-group" style="margin-top:var(--wp--preset--spacing--50)">

<!-- wp:query {"queryId":1,"query":{"perPage":100,"pages":0,"offset":0,"postType":"post","order":"desc","orderBy":"date","author":"","search":"","exclude":[],"sticky":"","inherit":false}} -->
<div class="wp-block-query">
    
    <!-- wp:post-template {"style":{"spacing":{"blockGap":"var:preset|spacing|50"}},"layout":{"type":"grid","columnCount":3}} -->
        <!-- wp:post-featured-image {"isLink":true,"aspectRatio":"1","style":{"spacing":{"margin":{"bottom":"var:preset|spacing|20"}}}} /-->
        <!-- wp:post-title {"isLink":true,"style":{"spacing":{"margin":{"top":"0"}}}} /-->
    <!-- /wp:post-template -->

    <!-- wp:query-pagination {"layout":{"type":"flex","justifyContent":"center"}} /-->

</div>
<!-- /wp:query -->

</main>
<!-- /wp:group -->

<!-- wp:template-part {"slug":"footer","tagName":"footer"} /-->
HTML;

        $result = wp_update_post([
            'ID' => $template->ID,
            'post_content' => $template_content
        ]);

        if ($result) {
            echo "✅ Updated template ID {$template->ID}<br>";
        } else {
            echo "❌ Failed to update ID {$template->ID}<br>";
        }
    }
}

if (function_exists('opcache_reset'))
    opcache_reset();
if (function_exists('wp_cache_flush'))
    wp_cache_flush();

echo "<br><a href='/'>Check Homepage</a>";
?>