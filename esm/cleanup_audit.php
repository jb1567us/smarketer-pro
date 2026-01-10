<?php
// cleanup_audit.php
$files = [
    'audit_and_fix_links.php',
    'audit_fix_v2.php',
    'audit_v3_json.php',
    'rescue_missing_zips.php',
    'cleanup_audit.php'
];

foreach ($files as $f) {
    if (file_exists(__DIR__ . '/' . $f)) {
        unlink(__DIR__ . '/' . $f);
        echo "Deleted $f<br>";
    }
}
?>