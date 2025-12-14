<?php
// cleanup_formatting.php
$files = [
    'fix_all_formatted_sql_final.php',
    'fix_work_party_formatted_sql.php',
    'fix_all_formatted_v2.php',
    'inspect_and_fix_work_party.php',
    'inspect_work_party.php',
    'cleanup_formatting.php'
];

foreach ($files as $f) {
    if (file_exists(__DIR__ . '/' . $f)) {
        unlink(__DIR__ . '/' . $f);
        echo "Deleted $f<br>";
    }
}
?>