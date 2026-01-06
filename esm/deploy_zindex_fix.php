<?php
// deploy_zindex_fix.php
// FIX INTERACTION ISSUES
// 1. Remove invalid 'display: flex' force on nav container (fixes "Stuck Open" menu)
// 2. Add Z-Index to Title/Logo (fixes "Not Clickable")

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
echo "<h1>🖱️ Deploying Interaction Fix (V4)</h1>";

$mu_dir = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/mu-plugins';

// --- CSS UPDATE (V4) ---
// Key Change: Removed 'display: flex !important' from .wp-block-navigation__responsive-container
// This allows the theme to hide it (Hamburger Mode) correctly.
$css_code = <<<'PHP'
<?php
/* Plugin Name: ESM Fixed Style V4 (Interaction Fix) */
/* Description: Fixed 180px Logo, Clickable Title, Working Hamburger */

add_action('wp_head', function() {
    echo '<style>
    /* 1. GLOBAL RESET & WIDTH FORCE */
    html, body {
        width: 100% !important;
        max-width: 100vw !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow-x: hidden !important;
    }

    /* 2. HEADER CONTAINER (Column Layout) */
    header .wp-block-group {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        width: 100% !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        position: relative !important;
        z-index: 50 !important; /* Base Z-Index */
    }

    /* 3. SITE TITLE (Clickable) */
    .wp-block-site-title {
        text-align: center !important;
        width: 100% !important;
        display: block !important;
        margin: 1rem 0 0.5rem 0 !important;
        position: relative !important;
        z-index: 101 !important; /* Above Overlay? */
        pointer-events: auto !important;
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

    /* 4. LOGO (FIXED 180px + Clickable) */
    .header-logo {
        display: block !important;
        margin: 0 auto 1.5rem auto !important;
        width: 180px !important; 
        max-width: 100% !important;
        position: relative !important;
        z-index: 101 !important;
        pointer-events: auto !important;
    }
    .header-logo img {
        display: block !important;
        margin: 0 auto !important;
        width: 100% !important;
        height: auto !important;
    }

    /* 5. NAVIGATION (RIGHT) */
    .wp-block-navigation {
        width: 100% !important;
        display: flex !important;
        flex-direction: row !important;
        justify-content: flex-end !important;
        padding-right: 2rem !important;
        box-sizing: border-box !important;
        position: relative !important;
        z-index: 100 !important;
    }
    
    /* FIX: DO NOT force display:flex on the CLOSED container. */
    /* Only ensure alignment when it IS open or for the button wrapper */
    .wp-block-navigation__responsive-container {
        margin-left: auto !important;
        margin-right: 0 !important;
        /* display: flex !important;  <-- REMOVED THIS LINE */
    }
    
    .wp-block-navigation__responsive-container-open {
        display: flex !important; /* Ok to force when open */
    }

    /* UTILS */
    .wp-block-post-title { display: none !important; }
    .wp-block-page-list { display: none !important; }
    </style>';
}, 999);
PHP;

file_put_contents($mu_dir . '/esm-fixed-logo-v4.php', $css_code);
echo "✅ Installed: esm-fixed-logo-v4.php (CSS Fxed)<br>";

// Cleanup V3
if (file_exists($mu_dir . '/esm-fixed-logo-v3.php')) {
    unlink($mu_dir . '/esm-fixed-logo-v3.php');
    echo "🧹 Removed V3 CSS.<br>";
}

if (function_exists('opcache_reset'))
    opcache_reset();
if (function_exists('wp_cache_flush'))
    wp_cache_flush();

echo "<a href='/fireworks/'>Check Interaction</a>";
?>