import base64
import os

ZIP_FILE = r'C:\sandbox\esm\sheets.zip'
PHP_OUT = r'C:\sandbox\esm\deploy_zip.php'

with open(ZIP_FILE, 'rb') as f:
    encoded = base64.b64encode(f.read()).decode('utf-8')

php_code = f"""<?php
$data = "{encoded}";
$decoded = base64_decode($data);
if (file_put_contents(__DIR__ . '/sheets.zip', $decoded)) {{
    echo "✅ Successfully deployed sheets.zip (" . strlen($decoded) . " bytes)";
}} else {{
    echo "❌ Failed to write sheets.zip";
}}
?>"""

with open(PHP_OUT, 'w', encoding='utf-8') as f:
    f.write(php_code)

print(f"Generated {PHP_OUT} with embedded zip data.")
