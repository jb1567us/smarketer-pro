<?php
// rebuild_theme_final.php
// FORCE REBUILD OF THEME FILES

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
$dir = WP_CONTENT_DIR . '/themes/esm-portfolio';

// 1. Clean functions.php
// Minimal setup, just enqueue styles
$funcs = <<<'PHP'
<?php
// ESM Portfolio Functions (Restored)

function esm_scripts() {
    wp_enqueue_style( 'esm-style', get_stylesheet_uri(), [], '1.0.1' );
}
add_action( 'wp_enqueue_scripts', 'esm_scripts' );

add_theme_support( 'title-tag' );
add_theme_support( 'post-thumbnails' );
PHP;
file_put_contents($dir . '/functions.php', $funcs);
echo "✅ Rebuilt functions.php<br>";

// 2. Clean header.php
$header = <<<'HTML'
<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
<meta charset="<?php bloginfo( 'charset' ); ?>">
<meta name="viewport" content="width=device-width, initial-scale=1">
<?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>
<div id="page" class="site">
	<header id="masthead" class="site-header">
		<h1 class="site-title"><a href="<?php echo esc_url( home_url( '/' ) ); ?>" rel="home"><?php bloginfo( 'name' ); ?></a></h1>
        <nav><?php wp_nav_menu( array( 'theme_location' => 'menu-1' ) ); ?></nav>
	</header>
    <div id="content" class="site-content">
HTML;
file_put_contents($dir . '/header.php', $header);
echo "✅ Rebuilt header.php<br>";

// 3. Clean footer.php
$footer = <<<'HTML'
    </div><!-- #content -->
	<footer id="colophon" class="site-footer">
        <p>&copy; <?php echo date('Y'); ?> <?php bloginfo( 'name' ); ?></p>
	</footer>
</div><!-- #page -->
<?php wp_footer(); ?>
</body>
</html>
HTML;
file_put_contents($dir . '/footer.php', $footer);
echo "✅ Rebuilt footer.php<br>";

// 4. Clean page.php with Buffer Clearing (Safety)
$page = <<<'PHP'
<?php
/**
 * The template for displaying all pages
 */
// Safety: Clear buffer if one exists from plugins
while (ob_get_level() > 0) { ob_end_clean(); }

get_header(); ?>

	<div id="primary" class="content-area">
		<main id="main" class="site-main">

		<?php
		while ( have_posts() ) :
			the_post();
            
            // Output content directly
            ?>
            <div class="artwork-page-container">
                <article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
                    <header class="entry-header">
                        <?php the_title( '<h1 class="entry-title">', '</h1>' ); ?>
                    </header>
                    <div class="entry-content">
                        <?php the_content(); ?>
                    </div>
                </article>
            </div>
            <?php

		endwhile; // End of the loop.
		?>

		</main><!-- #main -->
	</div><!-- #primary -->

<?php
get_footer();
PHP;
file_put_contents($dir . '/page.php', $page);
echo "✅ Rebuilt page.php<br>";

?>