<?php
// reinstall_core.php
// FORCE REINSTALL OF CORE FILES

set_time_limit(600);
ini_set('memory_limit', '512M');

$url = 'https://wordpress.org/latest.zip';
$zipFile = 'core_update.zip';
$extractPath = 'temp_core_update';

function rcopy($src, $dst)
{
    if (file_exists($dst))
        rrmdir($dst); // Nuke destination first to ensure clean state
    if (is_dir($src)) {
        mkdir($dst);
        $files = scandir($src);
        foreach ($files as $file) {
            if ($file != "." && $file != "..")
                rcopy("$src/$file", "$dst/$file");
        }
    } else if (file_exists($src)) {
        copy($src, $dst);
    }
}

function rrmdir($dir)
{
    if (is_dir($dir)) {
        $objects = scandir($dir);
        foreach ($objects as $object) {
            if ($object != "." && $object != "..") {
                if (is_dir($dir . "/" . $object) && !is_link($dir . "/" . $object))
                    rrmdir($dir . "/" . $object);
                else
                    unlink($dir . "/" . $object);
            }
        }
        rmdir($dir);
    } else {
        unlink($dir);
    }
}

echo "<h1>Starting Core Reinstall...</h1>";

// 1. Download
echo "Downloading $url...<br>";
$fp = fopen($zipFile, 'w+');
$ch = curl_init($url);
curl_setopt($ch, CURLOPT_TIMEOUT, 600);
curl_setopt($ch, CURLOPT_FILE, $fp);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
curl_exec($ch);
curl_close($ch);
fclose($fp);
echo "Download complete (Size: " . filesize($zipFile) . ")<br>";

// 2. Unzip
echo "Unzipping...<br>";
$zip = new ZipArchive;
if ($zip->open($zipFile) === TRUE) {
    $zip->extractTo($extractPath);
    $zip->close();
    echo "Unzip successful.<br>";
} else {
    die("❌ Unzip failed.");
}

$source = $extractPath . '/wordpress';
$root = $_SERVER['DOCUMENT_ROOT'];

// 3. Overwrite wp-admin
echo "Overwriting wp-admin... ";
rcopy($source . '/wp-admin', $root . '/wp-admin');
echo "Done.<br>";

// 4. Overwrite wp-includes
echo "Overwriting wp-includes... ";
rcopy($source . '/wp-includes', $root . '/wp-includes');
echo "Done.<br>";

// 5. Overwrite Root Files
echo "Overwriting root PHP files... ";
$files = scandir($source);
foreach ($files as $file) {
    if ($file == '.' || $file == '..')
        continue;
    if ($file == 'wp-content')
        continue; // SKIP CONTENT
    if ($file == 'wp-config.php')
        continue; // SKIP CONFIG (Shouldn't exist in zip but safe measure)

    if (is_file($source . '/' . $file)) {
        copy($source . '/' . $file, $root . '/' . $file);
        echo "$file ";
    }
}
echo "<br>";

// 6. Cleanup
echo "Cleaning up... ";
unlink($zipFile);
rrmdir($extractPath);
echo "Done.<br>";

echo "<h1>✅ CORE REINSTALL COMPLETE</h1>";
echo "Try loading the site now.";
?>