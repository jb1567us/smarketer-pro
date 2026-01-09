<?php
ini_set('display_errors', 1);
error_reporting(E_ALL);

require_once('wp-load.php'); // Ensure we can use WP functions

// 1. Delete WordPress Posts
$post_ids = [2070, 1912, 1913]; // In the Dark, Warm Glacier, Sunset Glacier
// Note: We DO NOT delete 1601 as it is used by the kept "Waves" page.

echo "<h1>Cleanup Artworks</h1>";

foreach ($post_ids as $pid) {
    if (wp_delete_post($pid, true)) {
        echo "Deleted Post ID: $pid<br>";
    } else {
        echo "Failed to delete Post ID: $pid (or it didn't exist)<br>";
    }
}

// 2. File Operations
$spec_dir = $_SERVER['DOCUMENT_ROOT'] . '/downloads/spec_sheets/';
$hires_dir = $_SERVER['DOCUMENT_ROOT'] . '/downloads/high_res/';

// Cleanup patterns
$patterns = [
    'In_the_Dark',
    'Warm_Glacier',
    'Sunset_Glacier',
    'Waves_Painting' // Cleanup old waves names if we are renaming
];

function delete_matching_files($dir, $patterns) {
    $files = scandir($dir);
    foreach ($files as $f) {
        if ($f == '.' || $f == '..') continue;
        foreach ($patterns as $p) {
            if (strpos($f, $p) === 0) { // Starts with pattern
                 // Special check for Waves to not delete if we want to rename, but we'll handle rename specifically
                 if (strpos($f, 'Waves_Painting') !== false) continue; // Skip Waves here, handle below
                 
                 if (unlink($dir . $f)) {
                     echo "Deleted file: $f<br>";
                 } else {
                     echo "Failed to delete: $f<br>";
                 }
            }
        }
    }
}

delete_matching_files($spec_dir, $patterns);
delete_matching_files($hires_dir, $patterns);

// 3. Rename Waves Files
// We want "Waves_Painting..." -> "Waves..."
// Original: Waves_Painting_Sheet.pdf -> Waves_Sheet.pdf
// Original: Waves_Painting_HighRes.zip -> Waves_HighRes.zip

$renames = [
    ['dir' => $spec_dir, 'from' => 'Waves_Painting_Sheet.pdf', 'to' => 'Waves_Sheet.pdf'],
    ['dir' => $hires_dir, 'from' => 'Waves_Painting_HighRes.zip', 'to' => 'Waves_HighRes.zip']
];

foreach ($renames as $r) {
    $old = $r['dir'] . $r['from'];
    $new = $r['dir'] . $r['to'];
    if (file_exists($old)) {
        if (rename($old, $new)) {
            echo "Renamed: {$r['from']} -> {$r['to']}<br>";
        } else {
            echo "Failed to rename: {$r['from']}<br>";
        }
    } else {
        echo "Source file not found for rename: {$r['from']}<br>";
        // Check if destination already exists
        if (file_exists($new)) {
             echo "Target file {$r['to']} already exists.<br>";
        }
    }
}

echo "Cleanup Complete.";
?>
