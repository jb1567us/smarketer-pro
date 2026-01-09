<?php
// diagnose_render_mock.php
// Manually simulate the theme rendering pipeline

ini_set('display_errors', 1);
error_reporting(E_ALL);

function trace($msg)
{
    echo "<div style='background:#eee;border:1px solid #ccc;padding:5px;margin:2px;'>[TRACE] $msg</div>";
    flush();
}

register_shutdown_function(function () {
    $error = error_get_last();
    if ($error && $error['type'] === E_ERROR) {
        echo "<h1 style='color:red'>💀 FATAL: " . $error['message'] . " in " . $error['file'] . ":" . $error['line'] . "</h1>";
    }
    echo "<h2>🛑 Script Shutdown</h2>";
});

require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');

$theme_dir = WP_CONTENT_DIR . '/themes/esm-portfolio';
trace("Theme Dir: $theme_dir");

// 1. Load Functions
trace("Step 1: Including functions.php");
include($theme_dir . '/functions.php');
trace("✅ Functions loaded.");

// 2. Load Header
// Mock get_header() behavior if needed, but let's try direct include first
// Note: native get_header() does `locate_template`.
trace("Step 2: Including header.php");
// We define a global post for context if needed
global $post;
$posts = get_posts(['numberposts' => 1]);
if ($posts) {
    $post = $posts[0];
    setup_postdata($post);
    trace("Setup post context: " . $post->post_title);
}

try {
    include($theme_dir . '/header.php');
} catch (Throwable $e) {
    trace("❌ EXCEPTION in header.php: " . $e->getMessage());
}
trace("✅ Header loaded (hopefully visible above).");

// 3. Load Page Body
trace("Step 3: Including page.php");
try {
    include($theme_dir . '/page.php');
} catch (Throwable $e) {
    trace("❌ EXCEPTION in page.php: " . $e->getMessage());
}
trace("✅ Page body loaded.");

// 4. Load Footer
trace("Step 4: Including footer.php");
try {
    include($theme_dir . '/footer.php');
} catch (Throwable $e) {
    trace("❌ EXCEPTION in footer.php: " . $e->getMessage());
}
trace("✅ Footer loaded.");

trace("🎉 COMPLETE PIPELINE FINISHED");
?>