<?php
// fix_infinite_loop.php
// Rebuild page.php WITHOUT the dangerous obfuscation buffer loop

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$dir = WP_CONTENT_DIR . '/themes/esm-portfolio';
if (!is_dir($dir))
    mkdir($dir, 0755, true);

// page.php (Premium Layout - NO LOOP)
$page = <<<'PHP'
<?php
/**
 * The template for displaying all pages
 */
// SAFE: No manual ob_clean loop here.
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
echo "<h1>✅ Rebuilt page.php (No Loop)</h1>";

// Force Activate to test immediately
$target = 'esm-portfolio';
update_option('template', $target);
update_option('stylesheet', $target);
if (function_exists('wp_cache_flush'))
    wp_cache_flush();

echo "Active Theme: " . get_option('stylesheet');
echo "<br><a href='/anemones/'>Check Anemones</a>";
?>