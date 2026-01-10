<?php
// Deploy Mobile & Camera Updates
// Source: c:\sandbox\esm\esm-trade-portal.php -> public_html/wp-content/plugins/esm-trade-portal/esm-trade-portal.php
// Source: c:\sandbox\esm\esm-trade-portal-v2.js -> public_html/wp-content/plugins/esm-trade-portal/esm-trade-portal-v2.js

$source_php = 'c:\sandbox\esm\esm-trade-portal.php';
$source_js = 'c:\sandbox\esm\esm-trade-portal-v2.js';

// Try standard paths first
$dest_php = 'c:\sandbox\esm\esm-portfolio-dev\wp-content\plugins\esm-trade-portal\esm-trade-portal.php';
$dest_js = 'c:\sandbox\esm\esm-portfolio-dev\wp-content\plugins\esm-trade-portal\esm-trade-portal-v2.js';

// Ensure destination dir exists
if (!file_exists(dirname($dest_php))) {
    mkdir(dirname($dest_php), 0777, true);
}

// Copy Files
if (copy($source_php, $dest_php)) echo "Deployed esm-trade-portal.php\n";
else echo "Failed to deploy esm-trade-portal.php\n";

if (copy($source_js, $dest_js)) echo "Deployed esm-trade-portal-v2.js\n";
else echo "Failed to deploy esm-trade-portal-v2.js\n";

// Bump version to force cache clear
$content = file_get_contents($dest_php);
$new_content = str_replace('v=2.1.2', 'v=2.2.0', $content); // Bump to 2.2.0
file_put_contents($dest_php, $new_content);
echo "Bumped version to 2.2.0\n";

// Create ZIP for manual upload just in case
$zip = new ZipArchive();
$zip_name = 'c:\sandbox\esm\mobile_deploy.zip';

if ($zip->open($zip_name, ZipArchive::CREATE | ZipArchive::OVERWRITE) === TRUE) {
    $zip->addFile($source_php, 'esm-trade-portal.php');
    $zip->addFile($source_js, 'esm-trade-portal-v2.js');
    $zip->close();
    echo "Created mobile_deploy.zip for manual upload.\n";
} else {
    echo "Failed to create ZIP.\n";
}
?>
