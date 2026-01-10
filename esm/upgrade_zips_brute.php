<?php
// upgrade_zips_brute.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
ini_set('max_execution_time', 600);
ini_set('memory_limit', '512M');

// Load Data
$jsonFile = $_SERVER['DOCUMENT_ROOT'] . '/artwork_data.json';
if (!file_exists($jsonFile))
    die("JSON file not found at $jsonFile");
$json = file_get_contents($jsonFile);
$artworks = json_decode($json, true);

if (!$artworks)
    die("Failed to load JSON");

$zip_dir = $_SERVER['DOCUMENT_ROOT'] . '/downloads/high_res/';

echo "<h1>Upgrading Zips (Brute Force Variants)</h1>";

$processed = 0;

foreach ($artworks as $art) {
    $title = $art['title'];
    $imgUrl = $art['image_url'] ?? '';

    if (empty($imgUrl))
        continue;

    // Determine Local Path from URL
    // URL: https://elliotspencermorgan.com/wp-content/uploads/2025/11/File.jpg
    $relPath = str_replace('https://elliotspencermorgan.com/', '', $imgUrl);
    $localPath = $_SERVER['DOCUMENT_ROOT'] . '/' . $relPath;

    if (!file_exists($localPath)) {
        // Try alternate path?
        continue; // Cannot find base file
    }

    $pathInfo = pathinfo($localPath);
    $dir = $pathInfo['dirname'];
    $filename = $pathInfo['filename']; // e.g. "Red_Planet"
    $ext = $pathInfo['extension'];

    // Scan directory for variants: filename-*.ext AND filename.ext
    // glob pattern: $dir/$filename*.$ext
    // Be careful not to verify "Red_Planet_Other.jpg" if it exists.
    // Variants usually have a hyphen or just strict suffix?
    // WP suffixes: -150x150, -300x300, -scaled, -rotated

    $candidates = glob($dir . '/' . $filename . '*.' . $ext);
    $files_to_zip = [];

    // Filter candidates to ensure they belong to this base
    // If base is "Art", glob "Art*" matches "Artwork". We don't want that.
    // Variants MUST start with "Art-" or be exactly "Art.ext".

    foreach ($candidates as $c) {
        $cName = pathinfo($c, 'filename');
        if ($cName === $filename || strpos($cName, $filename . '-') === 0) {
            $files_to_zip[basename($c)] = $c;
        }
    }

    // Create Zip
    if (count($files_to_zip) > 0) {
        // Calculate Zip Name from Title (Standard Logic)
        $cleanCtx = preg_replace('/[^\w\s-]/', '', $title);
        $cleanCtx = str_replace(' ', '_', trim($cleanCtx));
        $zipName = $cleanCtx . '_HighRes.zip';
        $zipPath = $zip_dir . $zipName;

        $zip = new ZipArchive();
        if ($zip->open($zipPath, ZipArchive::CREATE | ZipArchive::OVERWRITE) === TRUE) {
            foreach ($files_to_zip as $localName => $path) {
                $zip->addFile($path, $localName);
            }
            $zip->close();
            echo "📦 Zipped " . count($files_to_zip) . " files for: $title ($zipName)<br>";
            $processed++;
        }
    }

    if ($processed % 20 == 0)
        flush();
}

echo "Done. Processed $processed zips.";
?>