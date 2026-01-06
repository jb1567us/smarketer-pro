<?php
// raw_deploy_theme.php
// Cleanly overwrite ALL theme files (No WP Load)

$base = __DIR__ . '/wp-content/themes/esm-portfolio';
if (!is_dir($base))
    mkdir($base, 0755, true);

echo "<h1>🛠 Raw Theme Deployer</h1>";

// 1. functions.php (With Errors On)
$funcs = <<<'PHP'
<?php
// ESM Portfolio Functions (Clean v4 - Debug)
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

function esm_enqueues() {
    wp_enqueue_style( 'esm-style', get_stylesheet_uri(), [], time() );
}
add_action( 'wp_enqueue_scripts', 'esm_enqueues' );

add_theme_support( 'title-tag' );
add_theme_support( 'post-thumbnails' );
PHP;
file_put_contents("$base/functions.php", $funcs);
echo "✅ Wrote functions.php<br>";

// 2. style.css
$style = <<<'CSS'
/*
Theme Name: ESM Portfolio
Theme URI: https://elliotspencermorgan.com
Author: Antigravity
Description: Premium Restored v4
Version: 1.0.6
*/
body { background: #fff; color: #111; margin: 0; font-family: sans-serif; }
.site { max-width: 1400px; margin: 0 auto; }
.artwork-page-container { padding: 40px; border: 1px solid red; } /* Debug Border */
CSS;
file_put_contents("$base/style.css", $style);
echo "✅ Wrote style.css<br>";

// 3. header.php
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
		<h1>ESM Portfolio</h1>
	</header>
    <div id="content" class="site-content">
HTML;
file_put_contents("$base/header.php", $header);
echo "✅ Wrote header.php<br>";

// 4. footer.php
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
file_put_contents("$base/footer.php", $footer);
echo "✅ Wrote footer.php<br>";

// 5. index.php
file_put_contents("$base/index.php", '<?php get_header(); ?><h1>Index Template</h1><?php get_footer(); ?>');
echo "✅ Wrote index.php<br>";

// 6. page.php
$page = <<<'PHP'
<?php
get_header(); ?>
	<div id="primary" class="content-area">
		<main id="main" class="site-main">
		<?php
		while ( have_posts() ) :
			the_post();
            ?>
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
file_put_contents("$base/page.php", $page);
echo "✅ Wrote page.php<br>";

echo "<br><a href='/anemones/'>Check Site</a>";
?>