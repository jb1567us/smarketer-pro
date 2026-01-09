<?php
// restore_style.php
// Create mandatory style.css

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$dir = WP_CONTENT_DIR . '/themes/esm-portfolio';
if (!is_dir($dir))
    mkdir($dir, 0755, true);

$css = <<<'CSS'
/*
Theme Name: ESM Portfolio
Theme URI: https://elliotspencermorgan.com
Author: Antigravity
Description: Premium Portfolio Theme (Restored)
Version: 1.0.3
*/

body {
    background: #fff;
    color: #333;
    font-family: sans-serif;
}
.site {
    max-width: 1200px;
    margin: 0 auto;
}
.artwork-page-container {
    padding: 20px;
}
CSS;

file_put_contents($dir . '/style.css', $css);
echo "<h1>✅ Created style.css</h1>";
echo "view site: <a href='/anemones/'>/anemones/</a>";
?>