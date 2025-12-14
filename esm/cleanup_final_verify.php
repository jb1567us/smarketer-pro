<?php
// cleanup_final_verify.php
$files = [
    'verify_fix_final.php',
    'fix_global_blank_pages.php',
    'diagnose_blank.php',
    'cleanup_rescue_final.php',
    'cleanup_final_verify.php'
];

foreach ($files as $f) {
    if (file_exists(__DIR__ . '/' . $f)) {
        unlink(__DIR__ . '/' . $f);
        echo "Deleted $f<br>";
    }
}
?>