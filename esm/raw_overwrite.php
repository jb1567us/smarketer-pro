<?php
// raw_overwrite.php
// Directly overwrite functions.php WITHOUT loading WP core
// This prevents the active theme's die() from killing the repair script.

$path = __DIR__ . '/wp-content/themes/esm-portfolio/functions.php';

echo "<h1>🛠 Raw Overwrite Tool</h1>";
echo "Target: $path<br>";

if (!file_exists($path)) {
    die("❌ File not found (Check path?)");
}

$funcs = <<<'PHP'
<?php
// ESM Portfolio Functions (Clean v3)
// Restored by raw_overwrite.php

function esm_scripts() {
    wp_enqueue_style( 'esm-style', get_stylesheet_uri(), [], time() );
}
add_action( 'wp_enqueue_scripts', 'esm_scripts' );

add_theme_support( 'title-tag' );
add_theme_support( 'post-thumbnails' );
PHP;

$bytes = file_put_contents($path, $funcs);

if ($bytes) {
    echo "<h1>✅ Wrote $bytes bytes to functions.php</h1>";
    echo "The die() probe should be gone now.";
    echo "<br><a href='/anemones/'>Check Site</a>";
} else {
    echo "❌ Write Failed (Permissions?)";
}
?>