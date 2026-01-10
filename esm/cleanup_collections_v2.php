<?php
// cleanup_collections_v2.php
$files = [
    'fix_posts_to_pages.php',
    'collections_plan.md', // PHP won't delete this local file but good to track
    'fix_collection_links_force_sql.php',
    'fix_collection_links_final.php',
    'fix_collection_links_content.php',
    'debug_fix_collection.php',
    'inspect_collection_links.php',
    'inspect_collection_images.php',
    'investigate_collections.php',
    'cleanup_collections_v2.php',
    'cleanup_collections.php'
];

foreach ($files as $f) {
    if (file_exists(__DIR__ . '/' . $f)) {
        unlink(__DIR__ . '/' . $f);
        echo "Deleted $f<br>";
    }
}
?>