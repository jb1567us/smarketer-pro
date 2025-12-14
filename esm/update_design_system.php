<?php
// update_design_system.php
// Fixes "Menu Still in Center" issue by strengthening CSS

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
echo "<h1>🎨 Refining Design System (Nav Right Fix)</h1>";

$mu_dir = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/mu-plugins';
$master_file = $mu_dir . '/esm-design-system.php';

$plugin_code = <<<'PHP'
<?php
/* Plugin Name: ESM Design System (Consolidated) */

// 1. ENQUEUE FONTS
add_action('wp_enqueue_scripts', function() {
    wp_enqueue_style(
        'esm-google-fonts', 
        'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,400;0,600;1,400&display=swap', 
        [], 
        null
    );
});

// 2. RENDER FILTERS
add_filter('render_block_data', function($parsed_block) {
    if (isset($parsed_block['blockName']) && $parsed_block['blockName'] === 'core/navigation') {
        $parsed_block['attrs']['overlayMenu'] = 'always';
    }
    return $parsed_block;
}, 20, 1);

add_filter('render_block', function($block_content, $block) {
    if ($block['blockName'] === 'core/post-title') {
        if (is_singular() || is_page()) {
            return ''; 
        }
    }
    return $block_content;
}, 20, 2);


// 3. CSS (Fixing the Layout)
add_action('wp_head', function() {
    echo '<style>
    
    /* 1. HEADER CONTAINER FORCE (Vertical Stack) */
    header .wp-block-group {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        width: 100% !important;
    }

    /* 2. SITE TITLE (Centered) */
    .wp-block-site-title {
        text-align: center !important;
        width: 100% !important;
        display: block !important;
        margin-bottom: 0.5rem !important;
    }
    .wp-block-site-title a {
        font-family: "Playfair Display", serif !important;
        font-weight: 400 !important;
        text-decoration: none !important;
        font-size: 2.5rem !important;
        line-height: 1.2 !important;
        color: #1a1a1a !important;
        display: block !important;
        width: 100% !important;
        text-align: center !important;
    }

    /* 3. LOGO (Centered) */
    .header-logo {
        display: block !important;
        margin: 0 auto 1.5rem auto !important;
        max-width: 180px; /* Slight bump */
        height: auto;
    }
    .header-logo img {
        display: block;
        margin: 0 auto;
    }

    /* 4. NAVIGATION (RIGHT ALIGNED - REVISED) */
    /* The previous flex-end might have failed due to container width or parent 'align-items: center' */
    
    /* Force the Nav Block itself to fill width but align content right */
    .wp-block-navigation {
        width: 100% !important;
        display: flex !important;
        flex-direction: row !important;
        justify-content: flex-end !important; /* Force items to end */
        padding-right: 5vw !important; /* Responsive padding from right edge */
        box-sizing: border-box !important;
    }
    
    /* Force the inner container (the menu items/hamburger) to the right */
    .wp-block-navigation__responsive-container {
        margin-left: auto !important; /* This pushes it to the right */
        margin-right: 0 !important;
    }
    
    /* The Hamburger Button specifically */
    .wp-block-navigation__responsive-container-open {
        display: flex !important;
        margin-left: auto !important; /* Push to right */
        margin-right: 0 !important;
    }
    
    /* 5. UTILITIES */
    .wp-block-post-title { display: none !important; }
    .wp-block-page-list { display: none !important; }
    
    </style>';
}, 999);
PHP;

file_put_contents($master_file, $plugin_code);
echo "✅ Updated esm-design-system.php (Stronger Right-Nav CSS)<br>";

if (function_exists('wp_cache_flush'))
    wp_cache_flush();
if (function_exists('opcache_reset'))
    opcache_reset();

echo "<a href='/fireworks/'>Check /fireworks/</a>";
?>