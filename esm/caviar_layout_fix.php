<?php
// caviar_layout_fix.php
// 1. Force Safe Mode (DB)
// 2. Install MU-Plugin (Raw Write)

// Define Paths Relative to Public HTML Run
$root = __DIR__;
$mudir = $root . '/wp-content/mu-plugins';
if (!is_dir($mudir))
    mkdir($mudir, 0755, true);

echo "<h1>🐟 CAVIAR FIX v2</h1>";

// --- PART 1: MU PLUGIN ---
$plugin = <<<'PHP'
<?php
/*
Plugin Name: Caviar Layout Loader
Description: Hijack /anemones/ to show Premium Layout
*/

add_action('template_redirect', function() {
    // Only target Anemones
    if (strpos($_SERVER['REQUEST_URI'], '/anemones/') === false) {
        return;
    }

    // Connect to DB directly if global $wpdb fails, but we are inside WP here.
    global $wpdb;
    $content = $wpdb->get_var("SELECT post_content FROM $wpdb->posts WHERE ID = 213");
    
    if (!$content) $content = "<h1>Content Loading Error</h1>";

    // CSS Styling
    $css = <<<CSS
        <style>
            body { margin:0; padding:0; background:#fff; color:#333; font-family: 'Helvetica Neue', Helvetica, sans-serif; }
            .site-header { text-align:center; padding: 20px; border-bottom: 1px solid #eee; }
            .site-title a { text-decoration:none; color:#000; font-size:24px; }
            
            /* PREMIUM CAVIAR GRID */
            .artwork-page-container {
                max-width: 1200px;
                margin: 0 auto;
                padding: 40px;
                border: 0px solid green; /* Clean Look */
            }
            /* Add any other CSS classes detected in the HTML template here if missing */
        </style>
CSS;
    
    // OUTPUT
    echo '<!DOCTYPE html><html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">';
    echo '<title>Anemones – Elliot Spencer Morgan</title>';
    echo $css;
    echo '</head><body>';
    
    echo '<header class="site-header"><h1 class="site-title"><a href="/">Elliot Spencer Morgan</a></h1></header>';
    
    echo '<main>';
    echo '<div class="artwork-page-container">';
    echo do_shortcode($content); 
    echo '</div>';
    echo '</main>';
    
    echo '<footer style="text-align:center;padding:50px;color:#ccc;font-size:12px;">&copy; ' . date('Y') . ' ESM</footer>';
    echo '</body></html>';
    
    exit; // STOP THEME LOADING
}, 1); // Priority 1 (Early)
PHP;

file_put_contents($mudir . '/caviar-loader.php', $plugin);
echo "✅ MU-Plugin Installed.<br>";


// --- PART 2: FORCE SAFE MODE (RAW MYSQL) ---
// We must load WP to get DB creds, but we can't load standard stack if it crashes.
// Try SHORTINIT to fix DB without loading Theme
define('SHORTINIT', true);
require_once($root . '/wp-load.php');

if (isset($wpdb)) {
    $theme = 'twentytwentyfour';
    $wpdb->query("UPDATE $wpdb->options SET option_value = '$theme' WHERE option_name = 'template'");
    $wpdb->query("UPDATE $wpdb->options SET option_value = '$theme' WHERE option_name = 'stylesheet'");
    echo "✅ Switched DB to Safe Mode ($theme).<br>";
} else {
    echo "❌ DB Connect Failed (SHORTINIT).<br>";
}

echo "<a href='/anemones/'>Check Site</a>";
?>