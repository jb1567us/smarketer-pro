
import base64
import os

def get_base64_content(filepath):
    with open(filepath, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def generate_script():
    plugin_path = r'c:\sandbox\esm\esm-artwork-template.php'
    data_path = r'c:\sandbox\esm\artwork_data.json'
    
    plugin_b64 = get_base64_content(plugin_path)
    data_b64 = get_base64_content(data_path)
    
    # PHP Script Template
    php_content = f"""<?php
// finalize_deployment.php
// Auto-generated installer for ESM Artwork Template

header('Content-Type: text/html; charset=utf-8');
echo "<h1>🚀 Starting Deployment...</h1>";

function write_file_from_b64($path, $b64) {{
    $content = base64_decode($b64);
    if (file_put_contents($path, $content)) {{
        echo "✅ Wrote: $path<br>";
        return true;
    }} else {{
        echo "❌ Failed to write: $path<br>";
        return false;
    }}
}}

$mu_dir = WP_CONTENT_DIR . '/mu-plugins';
if (!is_dir($mu_dir)) {{
    mkdir($mu_dir, 0755, true);
    echo "Created directory: $mu_dir<br>";
}}

// 1. Install Plugin
if (write_file_from_b64($mu_dir . '/esm-artwork-template.php', '{plugin_b64}')) {{
    echo "Plugin installed.<br>";
}}

// 2. Install Data (to mu-plugins dir for encapsulation)
if (write_file_from_b64($mu_dir . '/artwork_data.json', '{data_b64}')) {{
    echo "Data file installed.<br>";
}}

// 3. Trigger Page Update (Caviar)
require_once(ABSPATH . 'wp-load.php');

$page = get_page_by_path('caviarpainting', OBJECT, 'page'); // Slug from previous convo
if (!$page) {{
    $page = get_page_by_title('Caviar');
}}

if ($page) {{
    $page_id = $page->ID;
    $updated_post = array(
        'ID'           => $page_id,
        'post_content' => '[esm_artwork_layout]',
    );
    wp_update_post($updated_post);
    echo "✅ Updated Page 'Caviar' (ID: $page_id) with shortcode.<br>";
}} else {{
    echo "⚠️ Could not find 'Caviar' page to update.<br>";
}}

// 4. Cleanup self (optional, maybe keep for log)
echo "<h2>✨ Deployment Complete!</h2>";
echo "<p>Please verify the <a href='/caviarpainting/'>Caviar Page</a>.</p>";
?>"""

    with open(r'c:\sandbox\esm\finalize_deployment.php', 'w', encoding='utf-8') as f:
        f.write(php_content)
    
    print("Generated c:\\sandbox\\esm\\finalize_deployment.php")

if __name__ == "__main__":
    generate_script()
