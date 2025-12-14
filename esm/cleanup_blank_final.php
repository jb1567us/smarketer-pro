<?php
// cleanup_blank_final.php
$files = [
    'fix_blank_structure_final_sql.php',
    'fix_blank_content_structure.php',
    'inspect_blank_page_v2.php',
    'inspect_blank_page.php',
    'cleanup_blank_final.php'
];

foreach ($files as $f) {
    if (file_exists(__DIR__ . '/' . $f)) {
        unlink(__DIR__ . '/' . $f);
        echo "Deleted $f<br>";
    }
}
?>