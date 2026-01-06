import base64
import os

source_file = r"c:\sandbox\esm\esm-trade-portal.php"
output_file = r"c:\sandbox\esm\deploy_portal_v14.php"

with open(source_file, "rb") as f:
    content = f.read()
    encoded = base64.b64encode(content).decode('utf-8')

php_content = f"""<?php
// Deploy Trade Portal v1.4
// Auto-generated deployment script

$b64 = "{encoded}";
$decoded = base64_decode($b64);
$file = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/mu-plugins/esm-trade-portal.php';

// Prepare dir
if (!is_dir(dirname($file))) {{
    mkdir(dirname($file), 0755, true);
}}

if (file_put_contents($file, $decoded)) {{
    echo "<div style='font-family:sans-serif; padding:20px; background:#e8f5e9; border:1px solid #c8e6c9;'>";
    echo "<h2>✅ Trade Portal v1.4 Deployed Successfully</h2>";
    echo "<p>File written to: <code>$file</code></p>";
    echo "<p>Size: " . strlen($decoded) . " bytes</p>";
    echo "<p><a href='/trade/' target='_blank' style='display:inline-block; padding:10px 20px; background:#2ecc71; color:white; text-decoration:none; border-radius:5px;'>Open Portal</a></p>";
    echo "</div>";
    
    // Attempt to flush rules
    if(function_exists('flush_rewrite_rules')) {{
        flush_rewrite_rules();
        echo "<p>Rewrite rules flushed.</p>";
    }}
}} else {{
    echo "<h2>❌ Failed to write file</h2>";
    echo "<p>Check permissions for " . dirname($file) . "</p>";
}}
?>"""

with open(output_file, "w") as f:
    f.write(php_content)

print(f"Generated {output_file}")
