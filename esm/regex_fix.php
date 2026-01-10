<?php
ini_set('display_errors', 1);
$file = 'wp-content/themes/esm-portfolio/functions.php';
$content = file_get_contents($file);

// Look for ?> followed by my specific comment
// We escape ? >
$pattern = '/\?>\s*(\/\/ Enable Tags for Pages)/';

if (preg_match($pattern, $content)) {
$new_content = preg_replace($pattern, "\n$1", $content); // Replace with newline + comment
if (file_put_contents($file, $new_content)) {
echo "SUCCESS: Found and removed the stray '?>'. Code should now execute.\n";
} else {
echo "ERROR: Failed to write file.\n";
}
} else {
echo "Pattern not found.\n";
$pos = strpos($content, "Enable Tags");
if ($pos !== false) {
// Show us what IS there before the comment
$start = max(0, $pos - 20);
$excerpt = substr($content, $start, 40);
echo "Context around 'Enable Tags': [" . htmlspecialchars($excerpt) . "]\n";

// Emergency fallback: Just strip ALL ?> found in the last 1000 chars?
// No, dangerous.
// Let's rely on the context to debug if this fails.
} else {
echo "Could not find 'Enable Tags' string at all.\n";
}
}
?>