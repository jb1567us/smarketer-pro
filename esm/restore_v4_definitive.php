<?php
// restore_v4_definitive.php
// ACTION: Enable SAFE plugins only (V4, Injector, Core)
// ACTION: Keep V6/V5 DISABLED

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
echo "<h1>🛡️ Restoring V4 Safe State</h1>";

$mu_dir = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/mu-plugins';

// List of files to ENABLE
$safe_plugins = [
    'esm-core-v2.php',
    'esm-fixed-logo-v4.php',
    'esm-logo-injector.php'
];

foreach ($safe_plugins as $plugin) {
    $off_file = $mu_dir . '/' . $plugin . '.off';
    $on_file = $mu_dir . '/' . $plugin;

    // Recovery: If .off exists, rename it back.
    if (file_exists($off_file)) {
        rename($off_file, $on_file);
        echo "✅ RESTORED: $plugin <br>";
    }
    // If not .off, maybe it wasn't disabled? Or doesn't exist?
    elseif (file_exists($on_file)) {
        echo "ℹ️ Already Active: $plugin <br>";
    } else {
        // If V4 doesn't exist (because we nuked it?), we recreate it.
        if ($plugin === 'esm-fixed-logo-v4.php') {
            echo "⚠️ V4 Missing, Re-Creating...<br>";
            // Insert V4 CSS Code here (Shortened for brevity, same as before)
            // Actually, better to just call the file write function again?
            // No, self-contained is better for these recovery scripts.
            $css_code_v4 = "<?php add_action('wp_head', function() { echo '<style>html,body{width:100%!important;max-width:100vw!important;overflow-x:hidden!important}header .wp-block-group{display:flex!important;flex-direction:column!important;align-items:center!important;position:relative!important;width:100%!important}.wp-block-site-title{text-align:center!important;width:100%!important;margin:1rem 0 0.5rem!important;z-index:101!important}.wp-block-site-title a{font-family:\"Playfair Display\",serif!important;font-size:2.5rem!important;color:#1a1a1a!important;text-decoration:none!important}.header-logo,.header-logo-injected img{display:block!important;margin:0 auto 1.5rem!important;width:180px!important;z-index:101!important}.wp-block-navigation{width:100%!important;display:flex!important;justify-content:flex-end!important;padding-right:2rem!important;z-index:100!important}.wp-block-navigation__responsive-container{margin-left:auto!important}.wp-block-post-title,.wp-block-page-list{display:none!important}</style>'; }, 999);";
            file_put_contents($on_file, $css_code_v4);
            echo "✅ RE-CREATED: $plugin <br>";
        } else {
            echo "❌ MISSING: $plugin (Upload manually if needed)<br>";
        }
    }
}

// ENSURE V6 is DEAD
if (file_exists($mu_dir . '/esm-fixed-logo-v6.php')) {
    rename($mu_dir . '/esm-fixed-logo-v6.php', $mu_dir . '/esm-fixed-logo-v6.php.DEAD');
    echo "💀 Killed Alive V6.<br>";
}

if (function_exists('opcache_reset'))
    opcache_reset();
if (function_exists('wp_cache_flush'))
    wp_cache_flush();

echo "<a href='/fireworks/'>Check Stability</a>";
?>