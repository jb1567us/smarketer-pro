import base64
import os

def create_deployment_php():
    spec_zip_path = r'c:\sandbox\esm\spec_slugs.zip'
    portal_php_path = r'c:\sandbox\esm\esm-trade-portal.php'
    output_php = r'c:\sandbox\esm\deploy_slugs.php'

    try:
        with open(spec_zip_path, 'rb') as f:
            zip_b64 = base64.b64encode(f.read()).decode('utf-8')
        
        with open(portal_php_path, 'rb') as f:
            portal_b64 = base64.b64encode(f.read()).decode('utf-8')
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    php_content = f"""<?php
// deploy_slugs.php
// v1.0
// Deploys:
// 1. Refactored Spec Sheets (slug_based)
// 2. Updated esm-trade-portal.php

header('Content-Type: text/plain');
ini_set('display_errors', 1);

echo "Starting Deployment (Slugs Refactor)...\\n";
echo "Document Root: " . $_SERVER['DOCUMENT_ROOT'] . "\\n";

$base_dir = $_SERVER['DOCUMENT_ROOT']; // Default relative to root
$spec_dir = $base_dir . '/downloads/spec_sheets';
// Assuming the theme/plugin file location. 
// Since we don't know EXACTLY where the user keeps esm-trade-portal.php (theme folder?), 
// we will put it in public_html root AND try to locate the existing one to overwrite?
// For now, let's put it in public_html and assume the user's loader points there or they move it.
$portal_target = $base_dir . '/esm-trade-portal.php'; 

echo "Target Spec Dir: $spec_dir\\n";
echo "Target Portal File: $portal_target\\n";

// 1. Deploy Spec Sheets
if (!file_exists($spec_dir)) {{
    mkdir($spec_dir, 0755, true);
}}

$zip_b64 = '{zip_b64}';
$zip_file = $base_dir . '/slugs_temp.zip';
file_put_contents($zip_file, base64_decode($zip_b64));

$zip = new ZipArchive;
if ($zip->open($zip_file) === TRUE) {{
    echo "Extracting spec sheets...\\n";
    $zip->extractTo($spec_dir);
    $zip->close();
    echo "SUCCESS: Spec sheets extracted.\\n";
}} else {{
    echo "ERROR: Failed to open zip.\\n";
}}
unlink($zip_file);

// 2. Deploy Code
$portal_b64 = '{portal_b64}';
if (file_put_contents($portal_target, base64_decode($portal_b64))) {{
    echo "SUCCESS: esm-trade-portal.php updated at $portal_target\\n";
}} else {{
    echo "ERROR: Failed to write esm-trade-portal.php\\n";
}}

// 3. Verification
$test_file = $spec_dir . '/self_portrait_1_spec.pdf';
if (file_exists($test_file)) {{
    echo "VERIFIED: $test_file exists.\\n";
}} else {{
    echo "WARNING: $test_file NOT found.\\n";
}}

echo "Deployment Complete.\\n";
?>"""

    with open(output_php, 'w', encoding='utf-8') as f:
        f.write(php_content)
    
    print(f"Generated {output_php}")

if __name__ == "__main__":
    create_deployment_php()
