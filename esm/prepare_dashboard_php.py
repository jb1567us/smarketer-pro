import json
import os
import base64

# Config
HTML_FILE = r'C:\sandbox\esm\client_dashboard.html'
PHP_OUTPUT = r'C:\sandbox\esm\deploy_dashboard.php'

def prepare_php_script():
    if not os.path.exists(HTML_FILE):
        print(f"Error: {HTML_FILE} not found.")
        return

    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Extract clean content (Body + Style)
    style_start = html_content.find('<style>')
    style_end = html_content.find('</style>') + 8
    style_block = html_content[style_start:style_end] if style_start > -1 else ""

    body_start = html_content.find('<body>') + 6
    body_end = html_content.find('</body>')
    body_content = html_content[body_start:body_end] if body_start > -1 else html_content

    final_content = f"{style_block}\n<div class='dashboard-wrapper'>{body_content}</div>"
    
    # Use Base64 to avoid all escaping issues
    b64_content = base64.b64encode(final_content.encode('utf-8')).decode('utf-8')

    php_code = f"""<?php
require_once('wp-load.php');

$secret = 'antigravity_deploy_2025';

// Allow access if user is admin OR if secret key is provided
$is_admin = current_user_can('edit_pages');
$has_key = isset($_GET['key']) && $_GET['key'] === $secret;

if (!$is_admin && !$has_key) {{
    die('Access Denied. You must be logged in as an admin or provide the correct query parameter.');
}}

$page_title = "Project Status";
$page_slug = "project-status";
// Decode content
$page_content = base64_decode('{b64_content}');

// Check if page exists
$page = get_page_by_path($page_slug);

$post_data = array(
    'post_title'    => $page_title,
    'post_content'  => $page_content,
    'post_status'   => 'publish',
    'post_type'     => 'page',
    'post_author'   => get_current_user_id() ? get_current_user_id() : 1, // Fallback to ID 1 if no user logged in
);

if ($page) {{
    $post_data['ID'] = $page->ID;
    $post_id = wp_update_post($post_data);
    echo "Updated existing page (ID: $post_id).<br>";
}} else {{
    $post_data['post_name'] = $page_slug;
    $post_id = wp_insert_post($post_data);
    echo "Created new page (ID: $post_id).<br>";
}}

if (is_wp_error($post_id)) {{
    echo "Error: " . $post_id->get_error_message();
}} else {{
    $permalink = get_permalink($post_id);
    echo "<strong>Success! Dashboard Deployed.</strong><br>";
    echo "View here: <a href='$permalink' target='_blank'>$permalink</a>";
}}

// Optional: Unlink self after success
// unlink(__FILE__);
?>"""

    with open(PHP_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(php_code)
    
    print(f"Generated {PHP_OUTPUT}")

if __name__ == "__main__":
    prepare_php_script()
