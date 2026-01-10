<?php
// Deploy script for Visualizer Preview Fix

$source = __DIR__ . '/esm-trade-portal.php';
$dest = '/home/elliotspencermor/public_html/content/plugins/esm-trade-portal/esm-trade-portal.php';

if (!file_exists($source)) {
    die("Error: Source file not found: $source\n");
}

// Read the new content
$new_content = file_get_contents($source);

// Function to upload via cPanel/FTP logic simulation (or direct file write if local context wraps remote)
// For this environment, we assume we can overwrite if we have access, otherwise we just output success for the automation tool
// But wait, the user's instructions imply we might need to *upload*. 
// Usually I create a PHP script that writes itself.

$deploy_script = <<<'EOD'
<?php
$target = '/home/elliotspencermor/public_html/content/plugins/esm-trade-portal/esm-trade-portal.php';
$content = base64_decode('%s');

if(file_put_contents($target, $content)) {
    echo "SUCCESS: Updated esm-trade-portal.php\n";
    echo "Size: " . filesize($target) . " bytes\n";
} else {
    echo "ERROR: Could not write to $target\n";
}
?>
EOD;

$deploy_payload = sprintf($deploy_script, base64_encode($new_content));
$deploy_file = __DIR__ . '/deploy_visualizer_fix.php';

file_put_contents($deploy_file, $deploy_payload);
echo "Created deployment script: $deploy_file\n";
?>
