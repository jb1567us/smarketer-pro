<?php
ini_set('display_errors', 1);
error_reporting(E_ALL);

$json_path = $_SERVER['DOCUMENT_ROOT'] . '/artwork_data.json';
$data = json_decode(file_get_contents($json_path), true);

$spec_dir = $_SERVER['DOCUMENT_ROOT'] . '/downloads/spec_sheets/';
$hires_dir = $_SERVER['DOCUMENT_ROOT'] . '/downloads/high_res/';

$missing_specs = [];
$missing_hires = [];

function find_file($dir, $candidates) {
    if (!is_dir($dir)) return false;
    foreach ($candidates as $c) {
        if (file_exists($dir . $c)) return $c;
    }
    return false;
}

echo "<h1>Download Link Verification</h1>";
echo "<p>Checking " . count($data) . " items...</p>";

foreach ($data as $item) {
    if ($item['type'] !== 'page' && $item['type'] !== 'post') continue;
    
    $title = trim($item['title']);
    $slug = $item['slug'] ?? 'NO_SLUG';
    
    // Ignore system pages
    if (stripos($title, 'Privacy Policy') !== false) continue;
    
    // Spec Search
    $candidates = [
        $title . '_spec.pdf',
        $slug . '_spec.pdf',
        str_replace(' ', '_', $title) . '_spec.pdf',
        $title . '_Sheet.pdf',
        $title . ' Painting_Sheet.pdf',
        str_replace(' ', '_', $title) . '_Sheet.pdf'
    ];
    $candidates = array_unique($candidates);
    
    $found_spec = find_file($spec_dir, $candidates);
    if (!$found_spec) {
        $missing_specs[] = $title;
    }
    
    // Zip Search
    $zip_candidates = [
        $title . '_HighRes.zip',
        $slug . '_HighRes.zip',
        str_replace(' ', '_', $title) . '_HighRes.zip',
        $title . ' Painting_HighRes.zip',
        str_replace(' ', '_', $title) . '_Painting_HighRes.zip'
    ];
    $zip_candidates = array_unique($zip_candidates);
    
    $found_zip = find_file($hires_dir, $zip_candidates);
    if (!$found_zip) {
        $missing_hires[] = $title;
    }
}

echo "Missing Spec Sheets (" . count($missing_specs) . "):\n";
foreach ($missing_specs as $m) echo "- $m\n";

echo "\nMissing High Res Zips (" . count($missing_hires) . "):\n";
foreach ($missing_hires as $m) echo "- $m\n";
?>
