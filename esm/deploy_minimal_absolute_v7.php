<?php
// deploy_minimal_absolute_v7.php
// MINIMAL CHANGE: Only nav position absolute
// Keep everything else from V4 exactly the same

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
echo "<h1>📌 Deploying Minimal V7 (Absolute Nav Only)</h1>";

$mu_dir = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/mu-plugins';

// V7: V4 + Minimal Absolute Nav Change
$css_code = <<<'PHPCODE'
<?php
/* Plugin Name: ESM Fixed Style V7 (Minimal Absolute) */
add_action('wp_head', function() {
echo '<style>
html,body{width:100%!important;max-width:100vw!important;margin:0!important;padding:0!important;overflow-x:hidden!important}
header .wp-block-group{display:flex!important;flex-direction:column!important;align-items:center!important;width:100%!important;padding-left:0!important;padding-right:0!important;position:relative!important;z-index:50!important}
.wp-block-site-title{text-align:center!important;width:100%!important;display:block!important;margin:1rem 0 0.5rem 0!important;position:relative!important;z-index:101!important;pointer-events:auto!important}
.wp-block-site-title a{font-family:"Playfair Display",serif!important;font-weight:400!important;font-size:2.5rem!important;line-height:1.2!important;color:#1a1a1a!important;display:block!important;width:100%!important;text-align:center!important;text-decoration:none!important}
.header-logo,.header-logo-injected img{display:block!important;margin:0 auto 1.5rem auto!important;width:180px!important;max-width:100%!important;position:relative!important;z-index:101!important;pointer-events:auto!important}
.wp-block-navigation{position:absolute!important;top:20px!important;right:20px!important;z-index:1000!important}
.wp-block-navigation__responsive-container-open{display:flex!important;position:fixed!important;top:0!important;left:0!important;right:0!important;bottom:0!important;width:100vw!important;height:100vh!important;background:#fff!important;z-index:99999!important;flex-direction:column!important;justify-content:center!important;padding:2rem!important}
.wp-block-post-title,.wp-block-page-list{display:none!important}
</style>';
}, 999);
PHPCODE;

file_put_contents($mu_dir . '/esm-fixed-logo-v7.php', $css_code);
echo "✅ Installed: esm-fixed-logo-v7.php<br>";

// Remove V4
if (file_exists($mu_dir . '/esm-fixed-logo-v4.php')) {
    unlink($mu_dir . '/esm-fixed-logo-v4.php');
    echo "🧹 Removed V4<br>";
}

if (function_exists('opcache_reset'))
    opcache_reset();
if (function_exists('wp_cache_flush'))
    wp_cache_flush();

echo "<a href='/fireworks/'>Check V7</a>";
?>