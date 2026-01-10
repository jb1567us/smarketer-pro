<?php
// restore_page.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$dir = get_stylesheet_directory();
$file = $dir . '/page.php';

$code = <<<'PHP'
<?php
/**
 * The template for displaying all pages
 */

get_header();
?>

<main id="primary" class="site-main">
    <?php
    while ( have_posts() ) :
        the_post();
        
        // Remove auto-p for these sensitive layouts if needed, 
        // but removing filter via plugin didn't work because loop was missing.
        // Now loop is back, standard wpautop applies.
        
        the_content();

    endwhile; // End of the loop.
    ?>
</main><!-- #main -->

<?php
get_footer();
PHP;

if (file_put_contents($file, $code)) {
    echo "✅ Restored page.php (" . filesize($file) . " bytes).<br>";
    echo "Path: $file";
} else {
    echo "❌ Failed to write to $file (Permissions?)";
}
?>