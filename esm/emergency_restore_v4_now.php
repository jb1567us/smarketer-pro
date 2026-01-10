<?php
// emergency_restore_v4_now.php
// IMMEDIATE REVERT: V7 hid the menu, restore V4

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
echo "<h1>🚑 Emergency Restore V4</h1>";

$mu_dir = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/mu-plugins';

// Delete V7
if (file_exists($mu_dir . '/esm-fixed-logo-v7.php')) {
    unlink($mu_dir . '/esm-fixed-logo-v7.php');
    echo "🧹 Removed V7<br>";
}

// Restore V4 (Full code, not compressed)
$css_code_v4 = <<<'PHP'
<?php
/* Plugin Name: ESM Fixed Style V4 (Safe Working Version) */
add_action('wp_head', function() {
    echo '<style>
    /* GLOBAL */
    html, body {
        width: 100% !important;
        max-width: 100vw !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow-x: hidden !important;
    }

    /* HEADER */
    header .wp-block-group {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        width: 100% !important;
        position: relative !important;
        z-index: 50 !important;
    }

    /* TITLE */
    .wp-block-site-title {
        text-align: center !important;
        width: 100% !important;
        display: block !important;
        margin: 1rem 0 0.5rem 0 !important;
        z-index: 101 !important;
        pointer-events: auto !important;
    }
    .wp-block-site-title a {
        font-family: "Playfair Display", serif !important;
        font-weight: 400 !important;
        font-size: 2.5rem !important;
        color: #1a1a1a !important;
        text-decoration: none !important;
    }

    /* LOGO */
    .header-logo, .header-logo-injected img {
        display: block !important;
        margin: 0 auto 1.5rem auto !important;
        width: 180px !important;
        max-width: 100% !important;
        z-index: 101 !important;
    }

    /* NAVIGATION (FLOW - RIGHT ALIGNED) */
    .wp-block-navigation {
        width: 100% !important;
        display: flex !important;
        justify-content: flex-end !important;
        padding-right: 2rem !important;
        z-index: 100 !important;
    }
    
    .wp-block-navigation__responsive-container-open {
        display: flex !important;
    }

    /* HIDE UTILS */
    .wp-block-post-title { display: none !important; }
    .wp-block-page-list { display: none !important; }
    </style>';
}, 999);
PHP;

file_put_contents($mu_dir . '/esm-fixed-logo-v4.php', $css_code_v4);
echo "✅ Restored V4<br>";

if (function_exists('opcache_reset'))
    opcache_reset();
if (function_exists('wp_cache_flush'))
    wp_cache_flush();

echo "<a href='/fireworks/'>Check V4</a>";
?>