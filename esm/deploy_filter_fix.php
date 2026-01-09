<?php
// Deploy Filter Fix
// Source: c:\sandbox\esm\esm-trade-portal.php -> public_html/wp-content/plugins/esm-trade-portal/esm-trade-portal.php

$source_php = 'c:\sandbox\esm\esm-trade-portal.php';
$dest_php = 'c:\sandbox\esm\esm-portfolio-dev\wp-content\plugins\esm-trade-portal\esm-trade-portal.php';

// Ensure destination dir exists (it should)
if (!file_exists(dirname($dest_php))) {
    mkdir(dirname($dest_php), 0777, true);
}

// Copy PHP
if (copy($source_php, $dest_php)) {
    echo "Deployed esm-trade-portal.php successfully.\n";
} else {
    echo "Failed to deploy esm-trade-portal.php\n";
}

// Bump version in file
$content = file_get_contents($dest_php);
$new_content = str_replace('v=2.1.1', 'v=2.1.2', $content);
file_put_contents($dest_php, $new_content);
echo "Bumped version to 2.1.2\n";

?>
