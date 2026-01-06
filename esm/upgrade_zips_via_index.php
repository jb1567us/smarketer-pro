<?php
// upgrade_zips_via_index.php
require_once($_SERVER['DOCUMENT_ROOT'] . '/wp-load.php');
ini_set('max_execution_time', 600);
ini_set('memory_limit', '512M');

echo "<h1>Upgrade Zips via Index</h1>";

// 1. Fetch the Index
$url = 'https://elliotspencermorgan.com/wp-content/uploads/2025/11-holdingspace-originals/';
// Use CURL to be safe
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, 1);
$html = curl_exec($ch);
curl_close($ch);

if (!$html) {
    die("Failed to fetch index: $url");
}

// 2. Parse Filenames
// Links look like: <a href="AnemonesPainting-150x150.jpg">...</a>
preg_match_all('/<a href="([^"]+\.jpg)">/i', $html, $matches);
$files = $matches[1];
$total_files = count($files);
echo "Found $total_files files in index.<br>";

// 3. Group by Base Name
// Heuristic: Base name is longest common prefix?
// Files: Name.jpg, Name-150x150.jpg, Name-updraft...
// Regex: Matches just Name part.
// Pattern: ^(.*?)(?:-\d+x\d+|-scaled|-updraft.*)?\.jpg$

$grouped = [];
foreach ($files as $f) {
    if (preg_match('/^(.*?)(?:-\d+x\d+|-scaled|-rotated|-updraft.*)?\.jpg$/i', $f, $m)) {
        $base = $m[1];
        // Clean base (sometimes weirdness)
        if (!isset($grouped[$base]))
            $grouped[$base] = [];
        $grouped[$base][] = $f;
    }
}

echo "Grouped into " . count($grouped) . " artworks.<br>";

// 4. Zip 'Em
$zip_dir = $_SERVER['DOCUMENT_ROOT'] . '/downloads/high_res/';
$processed = 0;
// We need to map Base Name back to Clean Title for Zip Name?
// Or just use Base Name for Zip?
// User format: [Title]_HighRes.zip.
// Our Base Name is from the FILENAME: e.g. "AnemonesPainting".
// We need to know which Zip corresponds to "AnemonesPainting".
// We can assume: `clean_title_for_zip` of the PAGE title matches the Base Filename?
// Not always.
// Strategy: Loop through our Artworks List (from JSON), calculate expected Zip Name.
// Find the matching Group in our file list.

$jsonFile = $_SERVER['DOCUMENT_ROOT'] . '/artwork_data.json';
if (!file_exists($jsonFile))
    die("JSON Missing");
$artworks = json_decode(file_get_contents($jsonFile), true);

foreach ($artworks as $art) {
    $title = $art['title'];
    $zipName = preg_replace('/[^\w\s-]/', '', $title);
    $zipName = str_replace(' ', '_', trim($zipName)) . '_HighRes.zip';

    // Find matching group
    // The image_url in JSON tells us the filename base!
    $imgUrl = $art['image_url'];
    if (!$imgUrl)
        continue;

    $pathInfo = pathinfo($imgUrl);
    $baseFilename = $pathInfo['filename']; // e.g. "AnemonesPainting"

    if (isset($grouped[$baseFilename])) {
        $filesToZip = $grouped[$baseFilename];

        $zipPath = $zip_dir . $zipName;
        $zip = new ZipArchive();
        if ($zip->open($zipPath, ZipArchive::CREATE | ZipArchive::OVERWRITE) === TRUE) {
            foreach ($filesToZip as $fName) {
                // Download content of file from URL?
                // Or use absolute path?
                // We know the dir path on server: .../wp-content/uploads/2025/11-holdingspace-originals/
                // But debugging failed to confirm it.
                // WE MUST USE CURL/FILE_GET_CONTENTS from the URL since local access failed.

                $fileUrl = $url . $fName;
                $content = @file_get_contents($fileUrl);
                if ($content) {
                    $zip->addFromString($fName, $content);
                }
            }
            $zip->close();
            echo "📦 Zipped: $zipName (" . count($filesToZip) . " variants)<br>";
            $processed++;
        }
    }

    if ($processed > 0 && $processed % 10 == 0)
        flush();
}

echo "Done. Processed $processed zips.";
?>