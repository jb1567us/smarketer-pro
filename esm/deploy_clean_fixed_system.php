<?php
// deploy_clean_fixed_system.php
// Re-installs the system with NEW filenames to ensure clean state.
// IMPORTS USER REQUIREMENT: Fixed 180px Logo.

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
echo "<h1>🛡️ Deploying Clean Fixed System V2</h1>";

$mu_dir = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/mu-plugins';
if (!is_dir($mu_dir)) {
    mkdir($mu_dir, 0755, true);
}

// --- 1. CORE LOGIC (Fonts + Attributes) ---
$core_code = <<<'PHP'
<?php
/* Plugin Name: ESM Core V2 (Safe) */
/* Description: Fonts, Hamburger Attribute, Title Removal */

// 1. FONTS
add_action('wp_enqueue_scripts', function() {
    wp_enqueue_style('esm-google-fonts', 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,400;0,600;1,400&display=swap', [], null);
});

// 2. HAMBURGER FORCE
add_filter('render_block_data', function($parsed_block) {
    if (isset($parsed_block['blockName']) && $parsed_block['blockName'] === 'core/navigation') {
        $parsed_block['attrs']['overlayMenu'] = 'always';
    }
    return $parsed_block;
}, 20, 1);

// 3. TITLE REMOVAL (Singular)
add_filter('render_block', function($block_content, $block) {
    if ($block['blockName'] === 'core/post-title') {
        if (is_singular() || is_page()) {
            return ''; 
        }
    }
    return $block_content;
}, 20, 2);
PHP;

file_put_contents($mu_dir . '/esm-core-v2.php', $core_code);
echo "✅ Installed: esm-core-v2.php<br>";


// --- 2. FIXED STYLING (User Request: 180px) ---
$style_code = <<<'PHP'
<?php
/* Plugin Name: ESM Fixed Style V2 */
/* Description: Fixed 180px Logo, Centered Header, Right Nav */

add_action('wp_head', function() {
    echo '<style>
    /* A. HEADER CONTAINER */
    header .wp-block-group {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        width: 100% !important; /* User Req: Not fixed width */
        max-width: 100% !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
    }

    /* B. SITE TITLE */
    .wp-block-site-title {
        text-align: center !important;
        width: 100% !important;
        display: block !important;
        margin: 1rem 0 0.5rem 0 !important;
    }
    .wp-block-site-title a {
        font-family: "Playfair Display", serif !important;
        font-weight: 400 !important;
        font-size: 2.5rem !important;
        line-height: 1.2 !important;
        color: #1a1a1a !important;
        display: block !important;
        width: 100% !important;
        text-align: center !important;
        text-decoration: none !important;
    }

    /* C. LOGO (FIXED 180px) */
    .header-logo {
        display: block !important;
        margin: 0 auto 1.5rem auto !important;
        width: 180px !important; /* FIXED as requested */
        max-width: 100% !important;
    }
    .header-logo img {
        display: block !important;
        margin: 0 auto !important;
        width: 100% !important; 
        height: auto !important;
    }

    /* D. NAVIGATION (RIGHT) */
    .wp-block-navigation {
        width: 100% !important;
        display: flex !important;
        flex-direction: row !important;
        justify-content: flex-end !important;
        padding-right: 2rem !important;
    }
    .wp-block-navigation__responsive-container,
    .wp-block-navigation__responsive-container-open {
        margin-left: auto !important;
        margin-right: 0 !important;
        display: flex !important;
    }

    /* E. UTILS */
    .wp-block-post-title { display: none !important; }
    .wp-block-page-list { display: none !important; }
    </style>';
}, 999);
PHP;

file_put_contents($mu_dir . '/esm-fixed-logo-v2.php', $style_code);
echo "✅ Installed: esm-fixed-logo-v2.php<br>";

// Cleanup OLD files just in case
$trash = glob($mu_dir . '/*.off');
foreach ($trash as $t) {
    unlink($t);
}

if (function_exists('opcache_reset'))
    opcache_reset();
echo "<a href='/fireworks/'>Check Recovery</a>";
?>