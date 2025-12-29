<?php
// Generates a self-contained deployment script for BOTH PHP and JS files

$files = [
    [
        'local' => __DIR__ . '/esm-trade-portal.php',
        'remote' => '/home/elliotspencermor/public_html/content/plugins/esm-trade-portal/esm-trade-portal.php'
    ],
    [
        'local' => __DIR__ . '/esm-trade-portal.js',
        'remote' => '/home/elliotspencermor/public_html/content/plugins/esm-trade-portal/esm-trade-portal.js'
    ]
];

$deploy_script_content = "<?php\n";
$deploy_script_content .= "echo '<pre>';\n";

foreach ($files as $file) {
    if (!file_exists($file['local'])) {
        die("Missing local file: " . $file['local']);
    }
    
    $content = file_get_contents($file['local']);
    $base64 = base64_encode($content);
    $dest = $file['remote'];
    
    $deploy_script_content .= "\n// Deploying to $dest\n";
    $deploy_script_content .= "\$dest = '$dest';\n";
    $deploy_script_content .= "\$content = base64_decode('$base64');\n";
    $deploy_script_content .= "if (file_put_contents(\$dest, \$content) !== false) {\n";
    $deploy_script_content .= "    echo 'Successfully updated: ' . \$dest . \"\\n\";\n";
    $deploy_script_content .= "} else {\n";
    $deploy_script_content .= "    echo 'ERROR: Failed to write to ' . \$dest . \"\\n\";\n";
    $deploy_script_content .= "}\n";
}

$deploy_script_content .= "echo '</pre>';\n";

$output_file = __DIR__ . '/deploy_full_visualizer.php';
file_put_contents($output_file, $deploy_script_content);

echo "Generated deployment script at: $output_file\n";
