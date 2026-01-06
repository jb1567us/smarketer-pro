<?php
// deploy_fixed_nav_v6.php
// FIX: Hamburger shifting down
// SOLUTION: Absolute Positioning with Overlap Protection (V6)
// DEPLOYS: esm-fixed-logo-v6.php

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
echo "<h1>📌 Deploying Absolute Nav V6 (Protected)</h1>";

$mu_dir = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/mu-plugins';

// --- CSS UPDATE (V6) ---
// Key Changes:
// 1. Nav Absolute (Top Right)
// 2. Open Menu Fixed (Full Screen)
// 3. Title Padding (Prevent Overlap)
$css_code = <<<'PHP'
<?php
/* Plugin Name: ESM Fixed Style V6 (Absolute Protected) */
/* Description: Fixed 180px Logo, Clickable Title, Absolute Nav V6 */

add_action('wp_head', function() {
    echo '<style>
    /* 1. GLOBAL RESET */
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
        padding: 20px 0 !important; /* General Padding */
        position: relative !important;
        z-index: 50 !important;
    }

    /* 3. SITE TITLE (Clickable + Safe) */
    .wp-block-site-title {
        text-align: center !important;
        width: 100% !important;
        display: block !important;
        margin: 0 0 1rem 0 !important; /* Reset Top Margin */
        padding: 0 50px !important; /* Prevent overlap with buttons */
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
    /* Responsive Title Size */
    @media (max-width: 600px) {
        .wp-block-site-title a { font-size: 1.8rem !important; }
        .wp-block-site-title { padding: 0 40px !important; } /* More space for button */
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
        width: auto !important; /* Don't take full width */
        height: auto !important;
        margin: 0 !important;
        padding: 0 !important;
        z-index: 1000 !important;
    }
    
    /* The Open Overlay MUST be Fixed to cover screen */
    .wp-block-navigation__responsive-container-open {
        display: flex !important;
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        bottom: 0 !important;
        right: 0 !important;
        width: 100vw !important;
        height: 100vh !important;
        background: #fff !important;
        z-index: 99999 !important; /* Highest Layer */
        flex-direction: column !important;
        justify-content: center !important;
        padding: 2rem !important;
    }

    /* Align "X" Close Button */
    .wp-block-navigation__responsive-container-close {
        position: absolute !important;
        top: 20px !important;
        right: 20px !important;
    }

    /* UTILS */
    .wp-block-post-title { display: none !important; }
    .wp-block-page-list { display: none !important; }
    </style>';
}, 999);
PHP;

file_put_contents($mu_dir . '/esm-fixed-logo-v6.php', $css_code);
echo "✅ Installed: esm-fixed-logo-v6.php (Absolute Protected)<br>";

// Cleanup V5/V4
if (file_exists($mu_dir . '/esm-fixed-logo-v5.php'))
    unlink($mu_dir . '/esm-fixed-logo-v5.php');
if (file_exists($mu_dir . '/esm-fixed-logo-v4.php'))
    unlink($mu_dir . '/esm-fixed-logo-v4.php');

if (function_exists('opcache_reset'))
    opcache_reset();
if (function_exists('wp_cache_flush'))
    wp_cache_flush();

echo "<a href='/fireworks/'>Check V6 Absolute</a>";
?>