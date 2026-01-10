<?php
// deploy_super_filter.php
// Install MU-Plugin to Intercept FSE Rendering

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$mu_dir = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/mu-plugins';
if (!is_dir($mu_dir)) {
    mkdir($mu_dir, 0755, true);
}

$plugin_code = <<<'PHP'
<?php
/* Plugin Name: Super FSE Fixer */

// 1. Force Navigation Attributes (Hamburger)
add_filter('render_block_data', function($parsed_block) {
    if (isset($parsed_block['blockName']) && $parsed_block['blockName'] === 'core/navigation') {
        // Enforce Hamburger
        $parsed_block['attrs']['overlayMenu'] = 'always';
        
        // Also force our Main Navigation ID if available?
        // We'll trust the Theme Template to point to a nav, OR the default Page List.
        // Even the Page List block inside Navigation should be hamburgered.
    }
    return $parsed_block;
}, 10, 1);


// 2. Remove Post Title (Double Title Fix)
add_filter('render_block', function($block_content, $block) {
    if ($block['blockName'] === 'core/post-title') {
        // Only on singular views (Pages/Posts) where content likely has its own title
        if (is_singular() || is_page()) {
            return ''; // Remove completely
        }
    }
    return $block_content;
}, 10, 2);

// 3. Extra CSS Just in Case
add_action('wp_head', function() {
    echo '<style>
    .wp-block-post-title { display: none !important; } 
    /* Force Hamburger Button if attributes fail */
    .wp-block-navigation__responsive-container-open { display: flex !important; }
    /* Hide the list if we forced the button */
    /* .wp-block-navigation__container { display: none; } -- Logic too risky for CSS only */
    </style>';
});
PHP;

file_put_contents($mu_dir . '/super-fse-fix.php', $plugin_code);
echo "✅ Installed Super FSE Fixer MU-Plugin.<br>";

// FLUSH
if (function_exists('wp_cache_flush'))
    wp_cache_flush();
if (function_exists('opcache_reset'))
    opcache_reset();

echo "<a href='/fireworks/'>Check /fireworks/</a>";
?>