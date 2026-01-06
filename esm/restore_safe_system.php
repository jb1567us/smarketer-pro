<?php
// restore_safe_system.php
// 1. Restore 'esm-design-system.php' to KNOWN GOOD state
// 2. Add 'esm-css-fixes.php' for the new CSS rules

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
echo "<h1>🛡️ Restoring Safe System + CSS Split</h1>";

$mu_dir = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/mu-plugins';
if (!is_dir($mu_dir)) {
    mkdir($mu_dir, 0755, true);
}

// --- PART 1: CORE LOGIC (Known Good) ---
// This file only handles Fonts and Logic filters. NO CSS.
$core_code = <<<'PHP'
<?php
/* Plugin Name: ESM Core Logic (Safe) */

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
PHP;

file_put_contents($mu_dir . '/esm-design-system.php', $core_code);
echo "✅ Restored Core Logic (esm-design-system.php)<br>";


// --- PART 2: CSS (The "Strong" Rules) ---
// Isolated in its own file.
$css_code = <<<'PHP'
<?php
/* Plugin Name: ESM CSS Overrides */
add_action('wp_head', function() {
    echo '<style>
    /* 1. HEADER CONTAINER (Vertical) */
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
        max-width: 180px; 
        height: auto;
    }
    .header-logo img {
        display: block;
        margin: 0 auto;
    }

    /* 4. NAVIGATION (RIGHT ALIGNED) */
    .wp-block-navigation {
        width: 100% !important;
        display: flex !important;
        flex-direction: row !important;
        justify-content: flex-end !important; 
        padding-right: 5vw !important;
        box-sizing: border-box !important;
    }
    .wp-block-navigation__responsive-container {
        margin-left: auto !important; 
        margin-right: 0 !important;
    }
    .wp-block-navigation__responsive-container-open {
        display: flex !important;
        margin-left: auto !important;
        margin-right: 0 !important;
    }
    
    /* 5. UTILITIES */
    .wp-block-post-title { display: none !important; }
    .wp-block-page-list { display: none !important; }
    </style>';
}, 999);
PHP;

file_put_contents($mu_dir . '/esm-css-fixes.php', $css_code);
echo "✅ Installed CSS Overrides (esm-css-fixes.php)<br>";

// Clean up .off files if any exist from emergency renames
$off_files = glob($mu_dir . '/*.off');
if ($off_files) {
    foreach ($off_files as $f) {
        unlink($f);
        echo "🧹 Cleaned up: " . basename($f) . "<br>";
    }
}

if (function_exists('opcache_reset'))
    opcache_reset();
if (function_exists('wp_cache_flush'))
    wp_cache_flush();

echo "<a href='/fireworks/'>Check /fireworks/</a>";
?>