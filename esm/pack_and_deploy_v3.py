import shutil
import os
import base64

# Zip the v3 sheets
# Output to sheets_v3.zip
shutil.make_archive('sheets_v3', 'zip', r'C:\sandbox\esm\spec_sheets_v3')
print("Created sheets_v3.zip")

# Create deployment script
SCRIPT_FILE = 'sheets_v3.zip'
PHP_OUT = 'deploy_sheets_v3.php'

with open(SCRIPT_FILE, 'rb') as f:
    encoded = base64.b64encode(f.read()).decode('utf-8')

php_code = f"""<?php
$data = "{encoded}";
$decoded = base64_decode($data);
$zip_file = __DIR__ . '/sheets_v3.zip';
$extract_path = __DIR__ . '/downloads/spec_sheets/';

if (file_put_contents($zip_file, $decoded)) {{
    echo "✅ Uploaded sheets_v3.zip (" . strlen($decoded) . " bytes)<br>";
    
    $zip = new ZipArchive;
    if ($zip->open($zip_file) === TRUE) {{
        if (!is_dir($extract_path)) mkdir($extract_path, 0755, true);
        $zip->extractTo($extract_path);
        $zip->close();
        echo "✅ Extracted to $extract_path<br>";
        
        // List a few files to verify
        $files = scandir($extract_path);
        echo "Files: " . implode(', ', array_slice($files, 2, 5)) . "...<br>";
        
        unlink($zip_file); // cleanup zip
    }} else {{
        echo "❌ Failed to open zip";
    }}
}} else {{
    echo "❌ Failed to write zip file";
}}
?>"""

with open(PHP_OUT, 'w', encoding='utf-8') as f:
    f.write(php_code)

print(f"Created {PHP_OUT}")
