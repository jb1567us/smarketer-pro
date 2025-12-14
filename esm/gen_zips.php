<?php
// gen_zips.php
ini_set('max_execution_time', 600); // 10 mins

$mapFile = __DIR__ . '/zip_map.json';
$outDir = __DIR__ . '/downloads/high_res/';

if (!file_exists($mapFile))
    die("❌ Missing zip_map.json");
if (!is_dir($outDir))
    mkdir($outDir, 0755, true);

$map = json_decode(file_get_contents($mapFile), true);
$count = 0;
$errors = 0;

echo "<pre>";
foreach ($map as $zipName => $source) {
    $zipPath = $outDir . $zipName;

    // Skip if exists? (Optional, maybe force overwrite)
    if (file_exists($zipPath) && filesize($zipPath) > 1000) {
        // echo "Skipping existing: $zipName\n"; 
        // continue;
    }

    $sourceContent = null;
    $localFile = '';
    $tempFile = false;

    // Check if URL or Local
    if (strpos($source, 'http') === 0) {
        // Remote URL (lookoverhere or other)
        $ctx = stream_context_create(['http' => ['timeout' => 5]]);
        $sourceContent = @file_get_contents($source, false, $ctx);
        if ($sourceContent) {
            $localFile = 'image.jpg'; // Name inside zip
        } else {
            echo "❌ Failed to download: $source\n";
            $errors++;
            continue;
        }
    } else {
        // Local path relative to root?
        // Source in map is "wp-content/..."
        $fullSource = __DIR__ . '/' . $source;
        if (file_exists($fullSource)) {
            $sourceContent = file_get_contents($fullSource);
            $localFile = basename($source);
        } else {
            echo "❌ Missing local file: $fullSource\n";
            $errors++;
            continue;
        }
    }

    // ZIP Creation
    if ($sourceContent) {
        $zip = new ZipArchive();
        if ($zip->open($zipPath, ZipArchive::CREATE | ZipArchive::OVERWRITE) === TRUE) {
            // Add file named nicely (Clean from zipname?)
            $niceName = str_replace(['_HighRes.zip', '_'], [' ', ' '], $zipName) . '.jpg';
            $zip->addFromString($niceName, $sourceContent);
            $zip->close();
            echo "✅ Created: $zipName\n";
            $count++;
        } else {
            echo "❌ Zip Error: $zipName\n";
            $errors++;
        }
    }
}
echo "Done. Created $count zips. Errors: $errors.\n";
?>