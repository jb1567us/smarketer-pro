
import base64
import os

def generate():
    # Read plugin code
    with open('esm-trade-portal.php', 'r', encoding='utf-8') as f:
        plugin_code = f.read()

    # Read JS code
    with open('esm-trade-portal.js', 'r', encoding='utf-8') as f:
        js_code = f.read()

    # Read image
    with open('istockphoto-1535511484-1024x1024.jpg', 'rb') as f:
        img_data = f.read()
        img_b64 = base64.b64encode(img_data).decode('utf-8')

    # Create PHP
    php_content = f"""<?php
// Deploy Visualizer Fix
$root = $_SERVER['DOCUMENT_ROOT'];

// 1. Deploy Image
$img_path = $root . '/istockphoto-1535511484-1024x1024.jpg';
$img_b64 = '{img_b64}';

if (file_put_contents($img_path, base64_decode($img_b64))) {{
    echo "<div style='color:green'>✅ Image deployed to $img_path</div>";
}} else {{
    echo "<div style='color:red'>❌ Failed to deploy image to $img_path</div>";
}}

// 2. Deploy Plugin
$plugin_path = $root . '/wp-content/mu-plugins/esm-trade-portal.php';
$plugin_code = <<<'PHP_EOD'
{plugin_code}
PHP_EOD;

if (!is_dir(dirname($plugin_path))) mkdir(dirname($plugin_path), 0755, true);

if (file_put_contents($plugin_path, $plugin_code)) {{
    echo "<div style='color:green'>✅ Plugin updated at $plugin_path</div>";
}} else {{
    echo "<div style='color:red'>❌ Failed to update plugin at $plugin_path</div>";
}}

// 3. Deploy JS
$js_path = $root . '/wp-content/mu-plugins/esm-trade-portal.js';
$js_code = <<<'JS_EOD'
{js_code}
JS_EOD;

if (file_put_contents($js_path, $js_code)) {{
    echo "<div style='color:green'>✅ JS updated at $js_path</div>";
}} else {{
    echo "<div style='color:red'>❌ Failed to update JS at $js_path</div>";
}}

echo "<br><a href='/trade/' style='padding:10px; background:#000; color:#fff; text-decoration:none'>Return to Trade Portal</a>";
?>"""

    with open('deploy_visualizer_fix.php', 'w', encoding='utf-8') as f:
        f.write(php_content)

    print("Generated deploy_visualizer_fix.php")

if __name__ == '__main__':
    generate()
