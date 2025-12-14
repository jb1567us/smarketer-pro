<?php
// final_cleanup_v2.php
$files = [
    'fix_all_force_sql.php',
    'nuke_cache.php',
    'fix_final_v2.php',
    'fix_final_verify.php',
    'fix_final_force.php',
    'fix_css_display.php',
    'fix_all_final.php',
    'fix_broken_collages.php',
    'check_status_final.php',
    'final_cleanup_v2.php'
];

foreach ($files as $f) {
    if (file_exists(__DIR__ . '/' . $f)) {
        unlink(__DIR__ . '/' . $f);
        echo "Deleted $f<br>";
    }
}
?>