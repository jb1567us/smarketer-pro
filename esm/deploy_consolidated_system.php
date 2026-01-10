<?php
// deploy_consolidated_system.php
// 1. Delete old/broken MU-Plugins
// 2. Install Single Unified "ESM Design System" Plugin

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
echo "<h1>🛡️ Deploying Consolidated Design System</h1>";

$mu_dir = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/mu-plugins';

// --- PART 1: CLEANUP ---
$trash_list = [
    'fse-style-fix.php.off',
    'fse-styles.php.off',
    'nuclear-styles.php.off',
    'super-fse-fix.php.off',
    'nuclear-styles.php', // Check for active ones too just in case
    'fse-styles.php',
    'super-fse-fix.php'
];

foreach ($trash_list as $f) {
    $path = $mu_dir . '/' . $f;
    if (file_exists($path)) {
        unlink($path);
        echo "🗑️ Deleted: $f<br>";
    }
}


// --- PART 2: UNIFIED PLUGIN CODE ---
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

// 2. RENDER FILTERS (Functionality)
add_filter('render_block_data', function($parsed_block) {
    // Force Hamburger
    if (isset($parsed_block['blockName']) && $parsed_block['blockName'] === 'core/navigation') {
        $parsed_block['attrs']['overlayMenu'] = 'always';
    }
    return $parsed_block;
}, 20, 1);

add_filter('render_block', function($block_content, $block) {
    // Remove Double Title on Singular Pages
    if ($block['blockName'] === 'core/post-title') {
        if (is_singular() || is_page()) {
            return ''; 
        }
    }
    return $block_content;
}, 20, 2);


// 3. NUCLEAR CSS (Layout & Typography)
add_action('wp_head', function() {
    echo '<style>
    /* A. Site Title (CENTER) */
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
        font-size: 2.2rem !important;
        line-height: 1.2 !important;
        color: #1a1a1a !important;
        display: block !important;
        width: 100% !important;
        text-align: center !important;
    }

    /* B. Logo (CENTER) */
    .header-logo {
        display: block !important;
        margin: 0 auto 1.5rem auto !important;
        max-width: 150px;
        height: auto;
    }
    .header-logo img {
        display: block;
        margin: 0 auto;
    }

    /* C. Navigation (RIGHT) */
    .wp-block-navigation {
        width: 100% !important;
        display: flex !important;
        justify-content: flex-end !important; /* RIGHT ALIGN */
        padding-right: 2rem; 
    }
    .wp-block-navigation__responsive-container-open {
        margin-left: auto !important; 
        display: flex !important;
    }
    
    /* D. Utilities */
    .wp-block-post-title { display: none !important; }
    .wp-block-page-list { display: none !important; }
    
    /* Vertical Stack Enforcement for Header Group */
    header .wp-block-group {
        flex-direction: column !important;
        align-items: center !important;
    }
    </style>';
}, 999);
PHP;

$master_file = $mu_dir . '/esm-design-system.php';
file_put_contents($master_file, $plugin_code);
echo "✅ Installed Master Plugin: esm-design-system.php<br>";

// FLUSH
if (function_exists('wp_cache_flush'))
    wp_cache_flush();
if (function_exists('opcache_reset'))
    opcache_reset();

echo "<a href='/fireworks/'>Check /fireworks/</a>";
?>