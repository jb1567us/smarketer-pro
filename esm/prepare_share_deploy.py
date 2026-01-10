import os

root = r"c:\sandbox\esm"
source_file = os.path.join(root, "esm-trade-portal.php")
output_file = os.path.join(root, "deploy_share_button.php")

with open(source_file, 'r', encoding='utf-8') as f:
    content = f.read()

php_script = f"""<?php
// Deploy Share Button
$root = $_SERVER['DOCUMENT_ROOT'];
$plugin_path = $root . '/wp-content/mu-plugins/esm-trade-portal.php';

$plugin_code = <<<'PHP_EOD'
{content}
PHP_EOD;

if (file_put_contents($plugin_path, $plugin_code)) {{
    echo "<div style='color:green'>✅ Plugin updated successfully at $plugin_path</div>";
    echo "<br><b>Share Button Logic Included.</b>";
}} else {{
    echo "<div style='color:red'>❌ Failed to update plugin at $plugin_path</div>";
}}
?>
"""

with open(output_file, 'w', encoding='utf-8') as f:
    f.write(php_script)

print(f"Generated {output_file}")
