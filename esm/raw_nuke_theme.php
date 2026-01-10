<?php
// raw_nuke_theme.php
// Delete ALL files in esm-portfolio without loading WP

$dir = __DIR__ . '/wp-content/themes/esm-portfolio';
echo "<h1>☢️ RAW NUKE THEME ☢️</h1>";
echo "Target: $dir<br>";

if (is_dir($dir)) {
    $files = scandir($dir);
    echo "<h3>Found Files:</h3><ul>";
    foreach ($files as $file) {
        if ($file === '.' || $file === '..')
            continue;
        $path = "$dir/$file";
        if (is_dir($path)) {
            // Simple recursive delete if needed, but assuming flat theme
            // Just rmdir?
        } else {
            if (unlink($path)) {
                echo "<li>Deleted: $file</li>";
            } else {
                echo "<li>❌ Failed to delete: $file</li>";
            }
        }
    }
    echo "</ul>";
} else {
    echo "Directory not found!<br>";
    mkdir($dir, 0755, true);
}

// NOW REBUILD CLEAN

// functions.php
$funcs = <<<'PHP'
<?php
// ESM Portfolio Functions (Clean v5 - Post-Nuke)
function esm_scripts() {
    wp_enqueue_style( 'esm-style', get_stylesheet_uri(), [], '1.0.7' );
}
add_action( 'wp_enqueue_scripts', 'esm_scripts' );
add_theme_support( 'title-tag' );
add_theme_support( 'post-thumbnails' );
PHP;
file_put_contents("$dir/functions.php", $funcs);

// style.css
$style = <<<'CSS'
/*
Theme Name: ESM Portfolio
Theme URI: https://elliotspencermorgan.com
Author: Antigravity
Description: Premium Restored v5
Version: 1.0.7
*/
body { background: #fff; color: #111; margin: 0; font-family: sans-serif; }
.site { max-width: 1400px; margin: 0 auto; }
.artwork-page-container { padding: 40px; border: 2px solid blue; }
CSS;
file_put_contents("$dir/style.css", $style);

// index.php
file_put_contents("$dir/index.php", '<?php get_header(); ?><h1>Index Fallback</h1><?php get_footer(); ?>');

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
		<h1>ESM Portfolio</h1>
	</header>
    <div id="content" class="site-content">
HTML;
file_put_contents("$dir/header.php", $header);

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

echo "<h1>✅ THEME REBORN (Clean Slate)</h1>";
echo "<a href='/anemones/'>Check Site</a>";
?>