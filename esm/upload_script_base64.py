import base64
import os

SCRIPT_FILE = r'C:\sandbox\esm\scan_images.php'
# Deploy as get_image_index.php
PHP_OUT = r'C:\sandbox\esm\deploy_scan.php'

with open(SCRIPT_FILE, 'rb') as f:
    encoded = base64.b64encode(f.read()).decode('utf-8')

php_code = f"""<?php
$data = "{encoded}";
$decoded = base64_decode($data);
if (file_put_contents(__DIR__ . '/get_image_index.php', $decoded)) {{
    echo "✅ Successfully deployed get_image_index.php (" . strlen($decoded) . " bytes)";
}} else {{
    echo "❌ Failed to write get_image_index.php";
}}
?>"""

with open(PHP_OUT, 'w', encoding='utf-8') as f:
    f.write(php_code)

print(f"Generated {PHP_OUT} with embedded script.")
