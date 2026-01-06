<?php
// debug_template_hierarchy.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
$dir = get_stylesheet_directory();

$files = [
    'page.php' => 'PAGE.PHP',
    'single.php' => 'SINGLE.PHP',
    'singular.php' => 'SINGULAR.PHP',
    'index.php' => 'INDEX.PHP'
];

foreach ($files as $f => $label) {
    $path = $dir . '/' . $f;
    $code = <<<PHP
<?php
echo "<h1 style='background:blue;color:white;padding:10px;'>DEBUG: LOADED $label</h1>";
get_header();
?>
<main id="primary" class="site-main">
    <?php
    if ( have_posts() ) :
        while ( have_posts() ) :
            the_post();
            echo "<h2>Loop in $label</h2>";
            the_content();
        endwhile;
    else :
        echo "<p>No posts in $label</p>";
    endif;
    ?>
</main>
<?php
get_footer();
PHP;

    file_put_contents($path, $code);
    echo "✅ Injected Debug into $f<br>";
}

// Flush Cache
if (function_exists('w3tc_flush_all'))
    w3tc_flush_all();
if (function_exists('wp_cache_flush'))
    wp_cache_flush();
echo "Flushed Caches.";
?>