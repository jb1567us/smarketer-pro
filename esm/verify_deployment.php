<?php
// verify_deployment.php
header('Content-Type: text/plain');

$files = [
    'esm-trade-portal.php',
    'esm-artwork-template.php',
    'esm-template-v3.php'
];

foreach ($files as $file) {
    echo "--- $file ---\n";
    if (!file_exists($file)) {
        echo "NOT FOUND\n";
        continue;
    }
    $content = file_get_contents($file);
    
    // Check for new patterns
    if (strpos($content, '_Sheet.pdf') !== false) {
        echo "Found new naming pattern (_Sheet.pdf)\n";
    } else {
        echo "Missing naming pattern (_Sheet.pdf)\n";
    }
    
    // Check for Trade Portal specific fix
    if ($file === 'esm-trade-portal.php') {
        if (strpos($content, '${item.title}_Sheet.pdf') !== false) {
             echo "Correct code: \${item.title}_Sheet.pdf\n";
        } else {
             echo "Old code found or missing update\n";
        }
    }

    // Check directory
    if (strpos($content, 'downloads/spec_sheets/') !== false) {
        echo "Correct directory found (downloads/spec_sheets/)\n";
    }
}
?>
