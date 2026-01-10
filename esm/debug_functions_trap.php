<?php
// debug_functions_trap.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
$dir = get_stylesheet_directory();
$file = $dir . '/functions.php';

$code = <<<'PHP'
<?php
// Emergency Debug Functions
add_action('wp_enqueue_scripts', function() {
    wp_enqueue_style( 'style', get_stylesheet_uri() );
});

add_filter('template_include', function($t) {
    echo "<h1 style='background:red;color:white;font-size:30px;z-index:99999;position:fixed;top:0;left:0;width:100%;height:100px;'>TEMPLATE: $t</h1>";
    die("<h1>DIED AT TEMPLATE INCLUDE</h1>");
});
PHP;

if (file_put_contents($file, $code)) {
    echo "✅ Replaced functions.php with Debug Trap.";
} else {
    echo "❌ Failed to write functions.php";
}
?>