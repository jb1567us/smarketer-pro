<?php
// nuclear_rebuild.php
// Delete and Rewrite ALL theme files to beat caching

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
$dir = WP_CONTENT_DIR . '/themes/esm-portfolio';

// 1. DELETE
echo "<h1>🔥 Deleting Old Files...</h1>";
$files = ['functions.php', 'style.css', 'index.php', 'page.php', 'header.php', 'footer.php'];
foreach ($files as $f) {
    if (file_exists("$dir/$f")) {
        unlink("$dir/$f");
        echo "Deleted $f<br>";
    }
}

// 2. WRITE FRESH

// functions.php
$funcs = <<<'PHP'
<?php
// ESM Portfolio Functions (Clean v2)
function esm_scripts() {
    wp_enqueue_style( 'esm-style', get_stylesheet_uri(), [], time() ); // Cache Busting time()
}
add_action( 'wp_enqueue_scripts', 'esm_scripts' );
add_theme_support( 'title-tag' );
add_theme_support( 'post-thumbnails' );
PHP;
file_put_contents($dir . '/functions.php', $funcs);

// style.css
$style = <<<'CSS'
/*
Theme Name: ESM Portfolio
Theme URI: https://elliotspencermorgan.com
Author: Antigravity
Description: Premium Restored
Version: 1.0.5
*/
body { background: #fff; color: #111; margin: 0; font-family: sans-serif; }
.site { max-width: 1400px; margin: 0 auto; }
.artwork-page-container { padding: 40px; }
CSS;
file_put_contents($dir . '/style.css', $style);

// index.php
file_put_contents($dir . '/index.php', '<?php get_header(); ?><h1>Index Fallback</h1><?php get_footer(); ?>');

// header.php
$header = <<<'HTML'
<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
<meta charset="<?php bloginfo( 'charset' ); ?>">
<meta name="viewport" content="width=device-width, initial-scale=1">
<?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<div id="page" class="site">
	<header id="masthead" class="site-header">
		<!-- Minimal Header -->
	</header>
    <div id="content" class="site-content">
HTML;
file_put_contents($dir . '/header.php', $header);

// footer.php
$footer = <<<'HTML'
    </div><!-- #content -->
	<footer id="colophon" class="site-footer">
        <p>&copy; 2025 ESM</p>
	</footer>
</div><!-- #page -->
<?php wp_footer(); ?>
</body>
</html>
HTML;
file_put_contents($dir . '/footer.php', $footer);

// page.php (Universal - No Loop)
$page = <<<'PHP'
<?php
get_header(); ?>
	<div id="primary" class="content-area">
		<main id="main" class="site-main">
		<?php
		while ( have_posts() ) :
			the_post();
            ?>
            <!-- PREMIUM CONTAINER MARKER -->
            <div class="artwork-page-container">
               <?php the_content(); ?>
            </div>
            <?php
		endwhile; 
		?>
		</main>
	</div>
<?php
get_footer();
PHP;
file_put_contents($dir . '/page.php', $page);

// OpCache Reset
if (function_exists('opcache_reset'))
    opcache_reset();

echo "<h1>✅ NUCLEAR REBUILD COMPLETE</h1>";
echo "view site: <a href='/anemones/'>/anemones/</a>";
?>