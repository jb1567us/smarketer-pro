<?php
// cleanup_final_v3.php
$files = [
    'upgrade_zips_via_index.php',
    'fix_pieces_red_force.php',
    'fix_all_double_links.php',
    'verify_zips_final.php',
    'upgrade_zips_batch.php',
    'upgrade_zips_brute.php',
    'upgrade_zips_multi.php',
    'upgrade_zips_v2.php',
    'fix_double_links_dom.php',
    'fix_double_links_sql.php',
    'fix_double_links_final_v2.php',
    'fix_double_links_final.php',
    'debug_pieces_red.php',
    'debug_pieces_red_v2.php',
    'debug_path.php',
    'scan_11.php',
    'scan_originals.php',
    'list_source_files.php',
    'investigate_variants_and_links.php',
    'check_zip_content.php',
    'verify_zip_content.php',
    'cleanup_final_v3.php'
];

foreach ($files as $f) {
    if (file_exists(__DIR__ . '/' . $f)) {
        unlink(__DIR__ . '/' . $f);
        echo "Deleted $f<br>";
    }
}
?>