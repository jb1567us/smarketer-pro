import base64
import os

def create_deployment_php():
    spec_zip_path = r'c:\sandbox\esm\spec_sheets.zip'
    json_path = r'c:\sandbox\esm\artwork_data.json'
    output_php = r'c:\sandbox\esm\deploy_v3.php'

    try:
        with open(spec_zip_path, 'rb') as f:
            zip_b64 = base64.b64encode(f.read()).decode('utf-8')
        
        with open(json_path, 'rb') as f:
            json_b64 = base64.b64encode(f.read()).decode('utf-8')
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    php_content = f"""<?php
// deploy_v3.php
// Deploys corrected spec sheets (Title Case, _spec.pdf) and artwork_data.json

header('Content-Type: text/plain');
echo "Script Version 3.0\n";
echo "DIR: " . __DIR__ . "\\n";

$zip_b64 = '{zip_b64}';
$json_b64 = '{json_b64}';

$base_dir = __DIR__;
$downloads_dir = $base_dir . '/downloads/spec_sheets';
$json_target = $base_dir . '/artwork_data.json';

// Ensure directory exists
if (!file_exists($downloads_dir)) {{
    mkdir($downloads_dir, 0755, true);
}}

// 1. Deploy JSON
echo "Deploying artwork_data.json...\\n";
$json_data = base64_decode($json_b64);
if (file_put_contents($json_target, $json_data)) {{
    echo "SUCCESS: artwork_data.json updated.\\n";
}} else {{
    echo "ERROR: Failed to write artwork_data.json to $json_target\\n";
}}

// 2. Deploy Spec Sheets
echo "Deploying Spec Sheets...\\n";
$zip_file = $base_dir . '/spec_sheets_temp.zip';
file_put_contents($zip_file, base64_decode($zip_b64));

$zip = new ZipArchive;
if ($zip->open($zip_file) === TRUE) {{
    // Cleanup old files first? Maybe safer to just overwrite since check failed
    // But user has _Sheet.pdf files we want to ignore/remove potentially
    
    // Unzip
    $zip->extractTo($downloads_dir);
    $zip->close();
    echo "SUCCESS: Spec sheets extracted to $downloads_dir\\n";
    unlink($zip_file);
}} else {{
    echo "ERROR: Failed to open zip file.\\n";
}}

// 3. Verify specific file
$test_file = $downloads_dir . '/Self Portrait 1_spec.pdf';
if (file_exists($test_file)) {{
    echo "VERIFIED: 'Self Portrait 1_spec.pdf' exists.\\n";
}} else {{
    echo "WARNING: 'Self Portrait 1_spec.pdf' NOT found.\\n";
}}

echo "Deployment Complete.\\n";
?>"""

    with open(output_php, 'w', encoding='utf-8') as f:
        f.write(php_content)
    
    print(f"Generated {output_php}")

if __name__ == "__main__":
    create_deployment_php()
