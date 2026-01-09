<?php
// cleanup_final.php
// Delete all temp files created during "Blank Page" debugging

$files = [
    'flush_opcache.php',
    'copy_functions_out.php',
    'check_post_status.php',
    'list_all_posts.php',
    'check_id_robust.php',
    'dump_all_templates.php',
    'dump_templates_safe.php',
    'delete_mu_rescue.php',
    'restore_header_footer.php',
    'kill_functions_again.php',
    'kill_all_plugins_final.php',
    'check_themes.php',
    'switch_theme_emergency.php',
    'check_error_log.php',
    'reinstall_core.php',
    'restore_theme_final.php',
    'restore_all_v2.php',
    'rebuild_theme_final.php',
    'check_anemones_content.php',
    'debug_templates_dump.txt',
    'funcs_dump.txt',
    'index_dump.txt',
    'temp_page.txt',
    'core_update.zip',
    'temp_core_update' // Directory
];

echo "<h1>Cleaning Up...</h1>";

foreach ($files as $f) {
    if (is_dir($f)) {
        // Recursive delete for dir not implemented here but temp_core_update should be gone
        if (rmdir($f))
            echo "✅ Deleted Dir: $f<br>";
        else
            echo "⚠️ Failed Dir: $f (might be empty or gone)<br>";
    } else {
        if (file_exists($f)) {
            if (unlink($f))
                echo "✅ Deleted: $f<br>";
            else
                echo "❌ Failed: $f<br>";
        } else {
            echo "ℹ️ Not Found: $f<br>";
        }
    }
}
echo "<h2>Done.</h2>";
?>