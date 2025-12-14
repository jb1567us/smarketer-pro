<?php
// deploy_caviar.php
// Deploy BRAND NEW theme directory "caviar-premium"

$dir = __DIR__ . '/wp-content/themes/caviar-premium';
if (!is_dir($dir))
    mkdir($dir, 0755, true);

echo "<h1>🐟 Deploying Caviar Premium 🐟</h1>";

// functions.php
$funcs = <<<'PHP'
<?php
// Caviar Premium Functions
function caviar_scripts() {
    wp_enqueue_style( 'caviar-style', get_stylesheet_uri() );
}
add_action( 'wp_enqueue_scripts', 'caviar_scripts' );
add_theme_support( 'title-tag' );
add_theme_support( 'post-thumbnails' );
PHP;
file_put_contents("$dir/functions.php", $funcs);

// style.css
$style = <<<'CSS'
/*
Theme Name: Caviar Premium
Theme URI: https://elliotspencermorgan.com
Author: Antigravity
Description: Fresh Start
Version: 1.0.0
*/
body { background: #fff; color: #111; font-family: sans-serif; }
.site { max-width: 1400px; margin: 0 auto; }
.artwork-page-container { padding: 40px; border: 5px solid gold; }
CSS;
file_put_contents("$dir/style.css", $style);

// index.php
file_put_contents("$dir/index.php", '<?php get_header(); ?><h1>Caviar Index</h1><?php get_footer(); ?>');

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
		<h1>Caviar Premium</h1>
	</header>
    <div id="content" class="site-content">
HTML;
file_put_contents("$dir/header.php", $header);

// footer.php
$footer = <<<'HTML'
    </div><!-- #content -->
	<footer id="colophon" class="site-footer">
        <p>&copy; 2025 Caviar</p>
	</footer>
</div><!-- #page -->
<?php wp_footer(); ?>
</body>
</html>
HTML;
file_put_contents("$dir/footer.php", $footer);

// page.php
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
file_put_contents("$dir/page.php", $page);

// Activate
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
if (function_exists('switch_theme')) {
    switch_theme('caviar-premium');
    echo "<h2>✅ Switched to Caviar Premium</h2>";
} else {
    update_option('template', 'caviar-premium');
    update_option('stylesheet', 'caviar-premium');
    echo "<h2>✅ ForcedDB Switch to Caviar Premium</h2>";
}

echo "<a href='/anemones/'>Check Site</a>";
?>