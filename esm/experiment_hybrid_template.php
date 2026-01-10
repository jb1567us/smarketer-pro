<?php
// experiment_hybrid_template.php
// Inject PHP template into Block Theme

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

// 1. Switch directly to twentytwentyfour (Safe Mode)
$theme = 'twentytwentyfour'; // Ensure this matches directory name exactly
switch_theme($theme);
echo "<h1>Activated: $theme</h1>";

// 2. Inject Template
$dir = WP_CONTENT_DIR . '/themes/' . $theme;
$file = $dir . '/page-anemones.php';

$code = <<<'PHP'
<?php
// HYBRID TEMPLATE
get_header(); 
?>
<style>
    .artwork-page-container {
        padding: 40px;
        background: #f0f0f0;
        border: 4px solid green;
    }
</style>
<div id="primary" class="content-area">
    <main id="main" class="site-main">
        <h1 style="color:red;font-size:40px;">🦖 HYBRID TEMPLATE ACTIVE</h1>
        <div class="artwork-page-container">
            <?php 
                if (have_posts()) {
                    while (have_posts()) {
                        the_post();
                        the_content();
                    }
                }
            ?>
        </div>
    </main>
</div>
<?php
get_footer();
?>
PHP;

file_put_contents($file, $code);
echo "<h1>✅ Injected page-anemones.php</h1>";
echo "view site: <a href='/anemones/'>/anemones/</a>";
?>