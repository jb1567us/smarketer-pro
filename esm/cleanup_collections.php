<?php
// cleanup_collections.php
$files = [
    'fix_collection_links_force_sql.php',
    'fix_collection_links_final.php',
    'fix_collection_links_content.php',
    'debug_fix_collection.php',
    'inspect_collection_links.php',
    'investigate_collections.php',
    'cleanup_collections.php'
];

foreach ($files as $f) {
    if (file_exists(__DIR__ . '/' . $f)) {
        unlink(__DIR__ . '/' . $f);
        echo "Deleted $f<br>";
    }
}
?>