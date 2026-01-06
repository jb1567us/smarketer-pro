import base64
import os

def generate_deploy_script():
    base_dir = r"c:\sandbox\esm"
    files_to_deploy = [
        ("esm-artwork-template.php", "wp-content/mu-plugins/esm-artwork-template.php"),
        ("mobile-spec.php", "mobile-spec.php"),
        ("esm-trade-portal.php", "wp-content/plugins/esm-trade-portal/esm-trade-portal.php")
    ]
    
    php_array_lines = []
    
    for filename, target_rel_path in files_to_deploy:
        local_path = os.path.join(base_dir, filename)
        if not os.path.exists(local_path):
            print(f"WARNING: File not found: {local_path}")
            continue
            
        with open(local_path, "rb") as f:
            content_b64 = base64.b64encode(f.read()).decode('utf-8')
            
        php_array_lines.append(f"    '{target_rel_path}' => '{content_b64}',")

    php_array_str = "\n".join(php_array_lines)

    php_script = f"""<?php
/**
 * ESM Deployment Script v2
 * Deploys multiple files to their correct locations.
 */

$files = [
{php_array_str}
];

$doc_root = $_SERVER['DOCUMENT_ROOT'];
echo "<pre>";
echo "<h2>ESM Deployment Log</h2>";
echo "Document Root: " . $doc_root . "\\n\\n";

foreach ($files as $rel_path => $content_b64) {{
    $dest = $doc_root . '/' . $rel_path;
    $dir = dirname($dest);
    
    if (!file_exists($dir)) {{
        echo "Creating directory: $dir\\n";
        if (!mkdir($dir, 0755, true)) {{
            echo "ERROR: Failed to create directory $dir\\n";
            continue;
        }}
    }}

    $content = base64_decode($content_b64);
    $result = file_put_contents($dest, $content);

    if ($result !== false) {{
        echo "SUCCESS: Wrote " . strlen($content) . " bytes to $dest\\n";
    }} else {{
        echo "ERROR: Failed to write to $dest (Check permissions)\\n";
    }}
}}

echo "\\n<strong>Deployment Complete.</strong>\\n";
echo "IMPORTANT: Please visit <a href='/wp-admin/options-permalink.php' target='_blank'>Settings > Permalinks</a> and click 'Save Components' to flush rewrite rules.\\n";
echo "</pre>";
?>
"""

    output_path = os.path.join(base_dir, "deploy_all.php")
    with open(output_path, "w") as f:
        f.write(php_script)
    
    print(f"Generated {output_path} with {len(files_to_deploy)} files.")

if __name__ == "__main__":
    generate_deploy_script()
