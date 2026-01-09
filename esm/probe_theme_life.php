<?php
// probe_theme_life.php
// Inject a die() probe into functions.php

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
$dir = WP_CONTENT_DIR . '/themes/esm-portfolio';

// Rebuild index.php just in case
file_put_contents($dir . '/index.php', '<?php get_header(); ?><h1>INDEX FALLBACK</h1><?php get_footer(); ?>');

// Probe functions.php
$funcs = <<<'PHP'
<?php
// PROBE: FUNCTIONS.PHP
if (!defined('ABSPATH')) exit;

// UNCOMMENT THIS TO TEST
die('<h1 style="color:green;font-size:50px;">🦖 THEME IS ALIVE (functions.php loaded)</h1>');

function esm_scripts() {
    wp_enqueue_style( 'esm-style', get_stylesheet_uri() );
}
add_action( 'wp_enqueue_scripts', 'esm_scripts' );
PHP;

file_put_contents($dir . '/functions.php', $funcs);

echo "<h1>✅ Probe Injected</h1>";
echo "view site: <a href='/anemones/'>/anemones/</a>";
?>