<?php
// debug_functions_advanced.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
$dir = get_stylesheet_directory();
$file = $dir . '/functions.php';

$code = <<<'PHP'
<?php
// Advanced Debug Trap

function emergency_dump($msg) {
    while (ob_get_level()) @ob_end_clean();
    echo "<h1 style='background:red;color:white;font-size:24px;padding:20px;border:5px solid black;position:relative;z-index:99999;'>$msg</h1>";
    flush(); 
}

add_action('init', function() {
    // Checkpoint 1: Init (Early)
    // emergency_dump("INIT ACTIVE"); // Uncomment if desperate, but expected to pass.
});

add_filter('template_include', function($template) {
    emergency_dump("TEMPLATE SELECTED: " . $template);
    die();
});

add_action('wp_head', function() {
     echo "<!-- WP HEAD FIRED -->";
}, 1);

add_action('shutdown', function() {
    // Checkpoint Last: Shutdown
    // emergency_dump("SHUTDOWN REACHED");
});
PHP;

if (file_put_contents($file, $code)) {
    echo "✅ Replaced functions.php with Advanced Trap.";
} else {
    echo "❌ Failed to write functions.php";
}
?>