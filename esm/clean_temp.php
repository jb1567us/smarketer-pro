<?php
// clean_temp.php
$files = [
    'gen_zips.php',
    'zip_map.json',
    'attach_highres_links.php',
    'cleanup_pages.php',
    'clean_temp.php' // Suicide logic (might fail if self-deleting while running)
];

foreach ($files as $f) {
    if (file_exists(__DIR__ . '/' . $f)) {
        unlink(__DIR__ . '/' . $f);
        echo "Deleted $f<br>";
    }
}
?>