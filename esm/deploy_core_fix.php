<?php
// deploy_core_fix.php
// FORCE REINSTALL OF CORE FILES ON SERVER

set_time_limit(600);
ini_set('memory_limit', '512M');
error_reporting(E_ALL);
ini_set('display_errors', 1);

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

echo "<h1>Starting Core Fix Deployment...</h1>";

if (file_exists('wp-settings.php') && file_exists('wp-includes/version.php')) {
    echo "<h3>✅ Core files seem present!</h3>";
    echo "Files checked: wp-settings.php, wp-includes/version.php<br>";
    echo "If you are still having issues, you can <a href='?force=1'>FORCE REINSTALL</a>";
    if (!isset($_GET['force'])) {
        exit;
    }
}

// 1. Download
echo "Downloading WordPress Core from $url...<br>";
$fp = fopen($zipFile, 'w+');
if (!$fp) {
    die("❌ Could not open $zipFile for writing. Check permissions.");
}

$ch = curl_init($url);
curl_setopt($ch, CURLOPT_TIMEOUT, 600);
curl_setopt($ch, CURLOPT_FILE, $fp);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
curl_exec($ch);
if (curl_errno($ch)) {
    die("❌ cURL Error: " . curl_error($ch));
}
curl_close($ch);
fclose($fp);
echo "Download complete (Size: " . filesize($zipFile) . " bytes)<br>";

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
$root = __DIR__;

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
        continue; // SKIP CONFIG
    if ($file == 'wp-config-sample.php')
        continue; 

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

echo "<h1>✅ DEPLOYMENT COMPLETE</h1>";
echo "Core files restored. Please check your site now.";
?>
