import base64
import os

def generate_json_deploy_script():
    base_dir = r"c:\sandbox\esm"
    json_path = os.path.join(base_dir, "artwork_data.json")
    
    with open(json_path, "rb") as f:
        json_content = base64.b64encode(f.read()).decode('utf-8')

    php_script = f"""<?php
/**
 * ESM JSON Deployment
 * Deploys artwork_data.json to Root and Plugin Dir
 */

$json_content = '{json_content}';
$doc_root = $_SERVER['DOCUMENT_ROOT'];

$locations = [
    $doc_root . '/artwork_data.json',
    $doc_root . '/wp-content/plugins/esm-trade-portal/artwork_data.json',
    $doc_root . '/wp-content/mu-plugins/artwork_data.json'
];

echo "<pre>";
echo "Deploying artwork_data.json...\\n";

foreach ($locations as $path) {{
    $dir = dirname($path);
    if (!file_exists($dir)) {{
        echo "Skipping $path (Directory missing)\\n";
        continue;
    }}
    
    $decoded = base64_decode($json_content);
    if (file_put_contents($path, $decoded)) {{
        echo "SUCCESS: Updated $path (" . strlen($decoded) . " bytes)\\n";
    }} else {{
        echo "ERROR: Failed to write to $path\\n";
    }}
}}

echo "\\nDone.";
echo "</pre>";
?>
"""
    output_path = os.path.join(base_dir, "deploy_json.php")
    with open(output_path, "w") as f:
        f.write(php_script)
    print(f"Generated {output_path}")

if __name__ == "__main__":
    generate_json_deploy_script()
