<?php
// rebuild_theme_stack.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
$dir = get_stylesheet_directory();

// 1. Minimum Viable Functions.php
$funcCode = <<<'PHP'
<?php
/**
 * ESM Portfolio Functions (Rebuilt)
 */
function esm_scripts() {
    wp_enqueue_style( 'esm-style', get_stylesheet_uri(), [], '1.0.0' );
}
add_action( 'wp_enqueue_scripts', 'esm_scripts' );

add_theme_support( 'title-tag' );
add_theme_support( 'post-thumbnails' );
add_theme_support( 'html5', array( 'search-form', 'gallery', 'caption' ) );

// Force Clear Buffers on Shutdown if needed
/* 
add_action('shutdown', function() {
    // keeping safe for now
});
*/
PHP;

if (file_put_contents($dir . '/functions.php', $funcCode)) {
    echo "✅ Rebuilt functions.php<br>";
} else {
    echo "❌ Failed to rebuild functions.php<br>";
}


// 2. Page.php with Buffer FLUSH
$pageCode = <<<'PHP'
<?php
/**
 * Page Template with Buffer Buster
 */

// CLEAR TRAPPED BUFFERS
while (ob_get_level() > 0) {
    ob_end_flush();
}

get_header(); ?>

<main id="primary" class="site-main artwork-page-container">
    <?php
    while ( have_posts() ) :
        the_post();
        ?>
        <article id="post-<?php the_ID(); ?>" <?php post_class(); ?>>
            <header class="entry-header">
                <h1 class="entry-title"><?php the_title(); ?></h1>
            </header>
            <div class="entry-content">
                <?php
                the_content();
                ?>
            </div>
        </article>
        <?php
    endwhile; // End of the loop.
    ?>
</main>

<?php
get_footer();
PHP;

if (file_put_contents($dir . '/page.php', $pageCode)) {
    echo "✅ Rebuilt page.php with Buffer Flush<br>";
    // Apply to single.php too
    copy($dir . '/page.php', $dir . '/single.php');
    echo "✅ Copied to single.php<br>";
}

?>