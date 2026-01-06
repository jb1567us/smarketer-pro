<?php
// emergency_disable_v6.php
// PURPOSE: Recover from Critical Error caused by V6
// ACTION: Delete V6, Restore V4 (Safe)

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
echo "<h1>🚑 Emergency Disable V6</h1>";

$mu_dir = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/mu-plugins';

// 1. DELETE CRASHING PLUGINS
$targets = [
    'esm-fixed-logo-v6.php',
    'esm-fixed-logo-v5.php',
    'esm-fixed-logo-v5.php.off', // Clean cleanup
];

foreach ($targets as $t) {
    if (file_exists($mu_dir . '/' . $t)) {
        unlink($mu_dir . '/' . $t);
        echo "✅ Deleted potentially crashing file: $t<br>";
    } else {
        echo "Note: $t not found.<br>";
    }
}

// 2. RESTORE V4 (Safe / Interaction Fixed)
// Re-writing V4 code just in case it was deleted.
$css_code_v4 = <<<'PHP'
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

    /* 3. SITE TITLE (Clickable) */
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

    /* 4. LOGO (FIXED 180px + Clickable) */
    .header-logo, .header-logo-injected img {
        display: block !important;
        margin: 0 auto 1.5rem auto !important;
        width: 180px !important; 
        max-width: 100% !important;
        position: relative !important;
        z-index: 101 !important;
        pointer-events: auto !important;
    }
    
    /* 5. NAVIGATION (Safe Flow - V4) */
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
    
    .wp-block-navigation__responsive-container {
        margin-left: auto !important;
        margin-right: 0 !important;
    }
    
    .wp-block-navigation__responsive-container-open {
        display: flex !important;
    }

    /* UTILS */
    .wp-block-post-title { display: none !important; }
    .wp-block-page-list { display: none !important; }
    </style>';
}, 999);
PHP;

file_put_contents($mu_dir . '/esm-fixed-logo-v4.php', $css_code_v4);
echo "✅ Restored: esm-fixed-logo-v4.php (Safe Layout)<br>";

// 3. CHECK ERROR LOG
$log_file = $_SERVER['DOCUMENT_ROOT'] . '/error_log';
if (file_exists($log_file)) {
    echo "<h3>Last 5 Errors:</h3><pre>";
    $lines = file($log_file);
    $last_5 = array_slice($lines, -5);
    foreach ($last_5 as $line) {
        echo htmlspecialchars($line);
    }
    echo "</pre>";
}

if (function_exists('opcache_reset'))
    opcache_reset();
if (function_exists('wp_cache_flush'))
    wp_cache_flush();

echo "<a href='/fireworks/'>Check Recovery</a>";
?>