<?php
ini_set('display_errors', 1);
error_reporting(E_ALL);

echo "<h1>Fixing Floating Sculpture Filenames</h1>";

$json_path = $_SERVER['DOCUMENT_ROOT'] . '/artwork_data.json';
$data = json_decode(file_get_contents($json_path), true);
$hires_dir = $_SERVER['DOCUMENT_ROOT'] . '/downloads/high_res/';

$floating_items = [];
foreach ($data as $item) {
    if (isset($item['title']) && stripos($item['title'], 'Floating') !== false) {
        $floating_items[] = trim($item['title']);
    }
}
$floating_items = array_unique($floating_items);

$files = scandir($hires_dir);
$server_files = [];
foreach ($files as $f) {
    if ($f != '.' && $f != '..') $server_files[] = $f;
}

foreach ($floating_items as $title) {
    echo "<h3>Processing: $title</h3>";
    // Calculate Target
    $target = str_replace(' ', '_', $title) . '_HighRes.zip';
    echo "Target: $target<br>";
    
    if (file_exists($hires_dir . $target)) {
        echo "<span style='color:green'>Target Exists!</span><br>";
        continue;
    }
    
    // Find candidate
    $candidate = null;
    $clean_title = str_replace([' ', '-', '_'], '', strtolower($title));
    
    foreach ($server_files as $f) {
        $clean_f = str_replace([' ', '-', '_', '_HighRes.zip'], '', strtolower($f));
        // Match base chars
        if ($clean_f === $clean_title) {
            $candidate = $f;
            break;
        }
        // Try without 'sculpture' in title matching file with sculpture?
        if (str_replace('sculpture', '', $clean_title) === $clean_f) {
             $candidate = $f; break;
        }
    }
    
    if ($candidate) {
        echo "Found Candidate: $candidate<br>";
        // Rename
        if (rename($hires_dir . $candidate, $hires_dir . $target)) {
            echo "<span style='color:blue'>RENAMED: $candidate -> $target</span><br>";
        } else {
            echo "<span style='color:red'>FAILED RENAME: $candidate</span><br>";
        }
    } else {
        echo "<span style='color:red'>NO CANDIDATE FOUND on server.</span><br>";
    }
}
?>
