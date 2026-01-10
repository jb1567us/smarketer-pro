<?php
// restore_page_debug.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
$dir = get_stylesheet_directory();
$file = $dir . '/page.php';

$code = <<<'PHP'
<?php
echo "<h1 style='background:red;color:white;padding:20px;'>DEBUG: PAGE LOADED</h1>";
get_header();
?>
<main id="primary" class="site-main">
    <h1>If you see this, Main is open.</h1>
    <?php
    if ( have_posts() ) :
        while ( have_posts() ) :
            the_post();
            echo "<h2>Loop Started</h2>";
            the_content();
            echo "<h2>Loop Ended</h2>";
        endwhile;
    else :
        echo "<p>No posts found.</p>";
    endif;
    ?>
</main>
<?php
get_footer();
PHP;

file_put_contents($file, $code);
echo "✅ Injected Debug into $file";
?>