import os

def generate_deployment_script():
    base_dir = r"c:\sandbox\esm"
    portal_php = os.path.join(base_dir, "esm-trade-portal.php")
    data_json = os.path.join(base_dir, "artwork_data.json")
    output_file = os.path.join(base_dir, "deploy_camera_update.php")
    
    with open(portal_php, "r", encoding="utf-8") as f:
        php_content = f.read()
        
    with open(data_json, "r", encoding="utf-8") as f:
        json_content = f.read()
        
    # Escape strings if necessary, but Nowdoc is safe for almost everything except the identifier itself at start of line
    # We use distinct identifiers
    
    script = f"""<?php
// Deploy Shrooms Fix
// Auto-generated

$portal_code = <<<'PHP_EOD'
{php_content}
PHP_EOD;

$json_data = <<<'JSON_EOD'
{json_content}
JSON_EOD;

$root = $_SERVER['DOCUMENT_ROOT'];
$plugin_file = $root . '/wp-content/mu-plugins/esm-trade-portal.php';
$json_file = $root . '/artwork_data.json';

// Deploy Plugin
if (!is_dir(dirname($plugin_file))) {{
    mkdir(dirname($plugin_file), 0755, true);
}}

$log = [];

if (file_put_contents($plugin_file, $portal_code)) {{
    $log[] = "✅ Plugin updated: $plugin_file (" . strlen($portal_code) . " bytes)";
}} else {{
    $log[] = "❌ Failed to write plugin file";
}}

// Deploy JSON
if (file_put_contents($json_file, $json_data)) {{
    $log[] = "✅ JSON updated: $json_file (" . strlen($json_data) . " bytes)";
}} else {{
    $log[] = "❌ Failed to write JSON file";
}}

echo "<div style='font-family:monospace; padding:20px; background:#fafafa; border:1px solid #ddd;'>";
foreach($log as $l) {{
    echo "<div>$l</div>";
}}
echo "<br><a href='/trade/' style='display:inline-block; padding:10px 20px; background:black; color:white; text-decoration:none;'>Go to Portal</a>";
echo "</div>";
?>
"""
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(script)
    
    print(f"Generated {output_file}")

if __name__ == "__main__":
    generate_deployment_script()
