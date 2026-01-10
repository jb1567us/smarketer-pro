<?php
// restore_functions_real.php
// Restore clean functions.php (No Probe)

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
$dir = WP_CONTENT_DIR . '/themes/esm-portfolio';

$funcs = <<<'PHP'
<?php
// ESM Portfolio Functions
function esm_scripts() {
    wp_enqueue_style( 'esm-style', get_stylesheet_uri(), [], '1.0.3' );
}
add_action( 'wp_enqueue_scripts', 'esm_scripts' );

// Support
add_theme_support( 'title-tag' );
add_theme_support( 'post-thumbnails' );
PHP;

file_put_contents($dir . '/functions.php', $funcs);

echo "<h1>✅ Functions Restored (Clean)</h1>";
echo "view site: <a href='/anemones/'>/anemones/</a>";
?>