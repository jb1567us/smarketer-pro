<?php
// force_direct_page.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
$dir = get_stylesheet_directory();
$file = $dir . '/page.php';

$code = <<<'PHP'
<?php
/**
 * DIRECT PAGE OUTPUT
 */
global $post;
echo "<div style='background:white;color:black;padding:50px;'>";
echo "<h1>DIRECT PAGE DEBUG</h1>";
if (isset($post->ID)) {
    echo "<h2>Post ID: " . $post->ID . "</h2>";
    echo "<h2>Title: " . $post->post_title . "</h2>";
    echo "<hr>";
    echo "<h3>Content:</h3>";
    $content = apply_filters('the_content', $post->post_content);
    echo $content;
} else {
    echo "<h1>NO GLOBAL POST OBJECT FOUND</h1>";
    global $wp_query;
    echo "<pre>";
    var_dump($wp_query);
    echo "</pre>";
}
echo "</div>";
die(); // Stop everything else
PHP;

if (file_put_contents($file, $code)) {
    echo "✅ Restored page.php with DIRECT DEBUG mode.";
} else {
    echo "❌ Failed to write page.php";
}
?>