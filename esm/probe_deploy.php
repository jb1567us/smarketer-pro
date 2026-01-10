
<?php
echo "<pre>";

// JS V3 CHECK
$target_js = "wp-content/plugins/esm-trade-portal/esm-trade-portal-v3.js";
if (file_exists($target_js)) {
    echo "V3 JS File Exists: $target_js\n";
    echo "Size: " . filesize($target_js) . "\n";
    $c = file_get_contents($target_js);
    if(strpos($c, 'touchstart') !== false) echo "  Status: TOUCH EVENTS PRESENT (Success)\n";
    else echo "  Status: TOUCH EVENTS MISSING (Failed)\n";
} else {
    echo "V3 JS File NOT FOUND at $target_js\n";
}

// PHP CHECK
$target_php = "wp-content/plugins/esm-trade-portal/esm-trade-portal.php";
if (file_exists($target_php)) {
    $c = file_get_contents($target_php);
    echo "PHP File: $target_php\n";
    if (strpos($c, 'esm-trade-portal-v3.js') !== false) echo "  Status: LOADING V3 SCRIPT (Success)\n";
    else echo "  Status: STILL LOADING OLD SCRIPT (Failed)\n";
} else {
    echo "PHP File NOT FOUND\n";
}

echo "</pre>";
?>
