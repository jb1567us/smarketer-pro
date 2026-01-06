<?php
// deploy_absolute_nav.php
// FIX: Hamburger Menu Shifting Down
// SOLUTION: Absolute Positioning (Top Right)
// DEPLOYS: esm-fixed-logo-v5.php

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
echo "<h1>📌 Deploying Absolute Nav Fix (V5)</h1>";

$mu_dir = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/mu-plugins';

// --- CSS UPDATE (V5) ---
// Key Change: .wp-block-navigation gets 'position: absolute; top: 1rem; right: 2rem;'
$css_code = <<<'PHP'
<?php
/* Plugin Name: ESM Fixed Style V5 (Absolute Nav) */
/* Description: Fixed 180px Logo, Clickable Title, Nav Pinned Top-Right */

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

    /* 2. HEADER CONTAINER (Relative Parent) */
    header .wp-block-group {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        width: 100% !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        position: relative !important;
        z-index: 50 !important;
    }

    /* 3. SITE TITLE (Centered) */
    .wp-block-site-title {
        text-align: center !important;
        width: 100% !important;
        display: block !important;
        margin: 1rem 0 0.5rem 0 !important;
        position: relative !important;
        z-index: 101 !important;
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

    /* 4. LOGO (FIXED 180px) */
    .header-logo, .header-logo-injected img {
        display: block !important;
        margin: 0 auto 1.5rem auto !important;
        width: 180px !important; 
        max-width: 100% !important;
        position: relative !important;
        z-index: 101 !important;
        pointer-events: auto !important;
    }

    /* 5. NAVIGATION (ABSOLUTE TOP RIGHT) */
    .wp-block-navigation {
        position: absolute !important;
        top: 20px !important;
        right: 20px !important;
        width: auto !important;
        height: auto !important;
        margin: 0 !important;
        padding: 0 !important;
        z-index: 1000 !important;
        display: flex !important;
        justify-content: flex-end !important;
        flex-direction: row !important;
    }
    
    /* Ensure Button Wrapper aligns right */
    .wp-block-navigation__responsive-container {
        margin-left: auto !important;
        margin-right: 0 !important;
    }
    
    .wp-block-navigation__responsive-container-open {
        display: flex !important;
        position: fixed !important; /* Full screen overlay needs fixed */
        top: 0 !important;
        left: 0 !important;
        bottom: 0 !important;
        right: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        background: #fff !important;
        z-index: 2000 !important;
        flex-direction: column !important;
        justify-content: center !important;
        padding: 2rem !important;
    }

    /* UTILS */
    .wp-block-post-title { display: none !important; }
    .wp-block-page-list { display: none !important; }
    </style>';
}, 999);
PHP;

file_put_contents($mu_dir . '/esm-fixed-logo-v5.php', $css_code);
echo "✅ Installed: esm-fixed-logo-v5.php (Absolute Nav)<br>";

// Cleanup V4
if (file_exists($mu_dir . '/esm-fixed-logo-v4.php')) {
    unlink($mu_dir . '/esm-fixed-logo-v4.php');
    echo "🧹 Removed V4 CSS.<br>";
}

if (function_exists('opcache_reset'))
    opcache_reset();
if (function_exists('wp_cache_flush'))
    wp_cache_flush();

echo "<a href='/fireworks/'>Check Absolute Nav</a>";
?>