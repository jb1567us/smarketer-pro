<?php
// rescue_mission_final.php
// ONE SCRIPT TO RULE THEM ALL
// 1. Rebuild Theme Files (Clean)
// 2. Force Activate Theme

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$dir = WP_CONTENT_DIR . '/themes/esm-portfolio';
if (!is_dir($dir))
    mkdir($dir, 0755, true);

echo "<h1>🚀 STARTING RESCUE MISSION</h1>";

// --- STEP 1: REBUILD FILES ---

// functions.php (Minimal Clean)
$funcs = <<<'PHP'
<?php
// ESM Portfolio Functions (Rescued)
function esm_scripts() {
    wp_enqueue_style( 'esm-style', get_stylesheet_uri(), [], '1.0.2' );
}
add_action( 'wp_enqueue_scripts', 'esm_scripts' );
add_theme_support( 'title-tag' );
add_theme_support( 'post-thumbnails' );
PHP;
file_put_contents($dir . '/functions.php', $funcs);
echo "✅ Rebuilt functions.php<br>";

// header.php (Minimal)
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
		<h1 class="site-title"><a href="<?php echo esc_url( home_url( '/' ) ); ?>" rel="home"><?php bloginfo( 'name' ); ?></a></h1>
        <nav><?php wp_nav_menu( array( 'theme_location' => 'menu-1' ) ); ?></nav>
	</header>
    <div id="content" class="site-content">
HTML;
file_put_contents($dir . '/header.php', $header);
echo "✅ Rebuilt header.php<br>";

// footer.php (Minimal)
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

// page.php (Premium Layout)
$page = <<<'PHP'
<?php
/**
 * The template for displaying all pages
 */
while (ob_get_level() > 0) { ob_end_clean(); } // Safety Buffer Clear
get_header(); ?>

	<div id="primary" class="content-area">
		<main id="main" class="site-main">
		<?php
		while ( have_posts() ) :
			the_post();
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
		endwhile; 
		?>
		</main>
	</div>

<?php
get_footer();
PHP;
file_put_contents($dir . '/page.php', $page);
echo "✅ Rebuilt page.php<br>";


// --- STEP 2: FORCE ACTIVATE ---

$target = 'esm-portfolio';
update_option('template', $target);
update_option('stylesheet', $target);

// Clear Caches
if (function_exists('wp_cache_flush'))
    wp_cache_flush();
if (function_exists('opcache_reset'))
    opcache_reset();

echo "<h1>✅ THEME ACTIVATED: " . get_option('stylesheet') . "</h1>";
echo "view site: <a href='/anemones/'>/anemones/</a>";
?>