<?php
ini_set('display_errors', 1);
$file = 'wp-content/themes/esm-portfolio/functions.php';
$content = file_get_contents($file);

// Construct regex safely to avoid closing this script early
$q = '?';
$gt = '>';
$pattern = '/' . '\\' . $q . $gt . '\s*(\/\/ Enable Tags)/';

if (preg_match($pattern, $content)) {
    // Replace with newline + comment group
    $new = preg_replace($pattern, "\n$1", $content);
    file_put_contents($file, $new);
    echo "SUCCESS: Found and removed the closing tag.";
} else {
    echo "Pattern not found.\n";
    // Check context
    $pos = strpos($content, "Enable Tags");
    if ($pos !== false) {
        $sub = substr($content, max(0, $pos - 10), 20);
        echo "Context: " . htmlspecialchars($sub);
    }
}
?>