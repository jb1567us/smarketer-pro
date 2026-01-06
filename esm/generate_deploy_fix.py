import base64
import os

def generate_fix_script():
    base_dir = r"c:\sandbox\esm"
    template_path = os.path.join(base_dir, "esm-artwork-template.php")
    
    with open(template_path, "rb") as f:
        content = base64.b64encode(f.read()).decode('utf-8')

    php_script = f"""<?php
/**
 * ESM Template Fix Deployment
 * Deploys esm-artwork-template.php and resets opcache
 */

$target = $_SERVER['DOCUMENT_ROOT'] . '/wp-content/mu-plugins/esm-artwork-template.php';
$content_b64 = '{content}';

echo "<pre>";
echo "Deploying to $target...\\n";

$decoded = base64_decode($content_b64);
if (file_put_contents($target, $decoded)) {{
    echo "SUCCESS: Wrote " . strlen($decoded) . " bytes.\\n";
}} else {{
    echo "ERROR: Failed to write file.\\n";
}}

if (function_exists('opcache_reset')) {{
    if (opcache_reset()) {{
        echo "SUCCESS: OpCache reset.\\n";
    }} else {{
        echo "WARNING: OpCache reset failed.\\n";
    }}
}} else {{
    echo "NOTE: OpCache not detected.\\n";
}}

echo "</pre>";
?>
"""
    output_path = os.path.join(base_dir, "deploy_template_fix.php")
    with open(output_path, "w") as f:
        f.write(php_script)
    print(f"Generated {output_path}")

if __name__ == "__main__":
    generate_fix_script()
