<?php
// Deploy Camera Update
// Source: c:\sandbox\esm\esm-trade-portal.php -> public_html/wp-content/plugins/esm-trade-portal/esm-trade-portal.php
// Source: c:\sandbox\esm\esm-trade-portal-v2.js -> public_html/wp-content/plugins/esm-trade-portal/esm-trade-portal-v2.js

$source_php = 'c:\sandbox\esm\esm-trade-portal.php';
$source_js = 'c:\sandbox\esm\esm-trade-portal-v2.js';

$dest_php = 'c:\sandbox\esm\esm-portfolio-dev\wp-content\plugins\esm-trade-portal\esm-trade-portal.php';
$dest_js = 'c:\sandbox\esm\esm-portfolio-dev\wp-content\plugins\esm-trade-portal\esm-trade-portal-v2.js';

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

// Copy JS
if (copy($source_js, $dest_js)) {
    echo "Deployed esm-trade-portal-v2.js successfully.\n";
} else {
    echo "Failed to deploy esm-trade-portal-v2.js\n";
}

// Also Update current version version query string in PHP file if we want to force cache bust
// For now, I'll trust the user to hard refresh or just append a random string if needed.
// But the code has ?v=2.1.0. Let's start using 2.1.1 to be safe.

$content = file_get_contents($dest_php);
$new_content = str_replace('v=2.1.0', 'v=2.1.1', $content);
file_put_contents($dest_php, $new_content);
echo "Bumped version to 2.1.1\n";

?>
