<?php
// fix_critical_revert_logo.php
// Reverts to fixed 180px width to stabilize the site.
// USES ABSOLUTE URLS for safety.

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
echo "<h1>🛡️ REVERTING to Fixed Stability</h1>";

$mu_dir = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/mu-plugins';
$css_file = $mu_dir . '/esm-css-fixes.php';

// CSS: Back to 180px fixed width (User Request) but safe syntax
// We keep the container full width to avoid layout locking, but clamp the logo.
$css_code = <<<'PHP'
<?php
/* Plugin Name: ESM CSS Overrides (Stable Revert) */
add_action('wp_head', function() {
    echo '<style>
    /* 1. HEADER CONTAINER (Vertical & Full Width) */
    header .wp-block-group {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        width: 100% !important; 
        max-width: 100% !important;
    }

    /* 2. SITE TITLE */
    .wp-block-site-title {
        text-align: center !important;
        width: 100% !important;
        display: block !important;
        margin: 1rem 0 0.5rem 0 !important;
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

    /* 3. LOGO (FIXED 180px - USER REQUEST) */
    .header-logo {
        display: block !important;
        margin: 0 auto 1.5rem auto !important;
        width: 180px !important; /* FIXED */
        max-width: 100% !important;
    }
    .header-logo img {
        display: block !important;
        margin: 0 auto !important;
        width: 100% !important;
        height: auto !important;
    }

    /* 4. NAVIGATION (Right Aligned) */
    .wp-block-navigation {
        width: 100% !important;
        display: flex !important;
        flex-direction: row !important;
        justify-content: flex-end !important; 
        padding-right: 2rem !important;
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
    
    /* Utilities */
    .wp-block-post-title { display: none !important; }
    .wp-block-page-list { display: none !important; }
    </style>';
}, 999);
PHP;

file_put_contents($css_file, $css_code);
echo "✅ Restored CSS to Fixed 180px Width.<br>";

if (function_exists('opcache_reset'))
    opcache_reset();
echo "<a href='/fireworks/'>Check Recovery</a>";
?>