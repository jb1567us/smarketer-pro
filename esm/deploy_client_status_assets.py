import sys
import os
import base64

# Add webhost-automation to path
sys.path.insert(0, r"c:\sandbox\esm\webhost-automation")

try:
    from webhost_automation.config import Config
    from webhost_automation.browser_bot import BrowserBot
    from dotenv import load_dotenv
except ImportError:
    print("Error: Could not import webhost_automation modules. Make sure the directory exists.")
    sys.exit(1)

def generate_dashboard_deployer():
    html_path = r"c:\sandbox\esm\client_dashboard.html"
    output_php = r"c:\sandbox\esm\deploy_dashboard_update.php"
    
    with open(html_path, "rb") as f:
        html_content = f.read()
    
    b64_content = base64.b64encode(html_content).decode('utf-8')
    
    php_template = f"""<?php
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

// unlink(__FILE__);
?>"""

    with open(output_php, "w", encoding='utf-8') as f:
        f.write(php_template)
    
    return output_php

def main():
    try:
        # Generate the PHP deployer for the dashboard
        print("Generating dashboard deployer...")
        dashboard_php = generate_dashboard_deployer()
        
        # Template file
        template_php = r"c:\sandbox\esm\wp-content\themes\caviar-premium\page-client-status.php"

        # Initialize BrowserBot
        os.chdir(r"c:\sandbox\esm\webhost-automation")
        load_dotenv(".env")
        config = Config()
        config.validate()
        
        print("Initializing BrowserBot...")
        bot = BrowserBot(config, headless=True) # Run headless for speed
        
        # Upload Dashboard Deployer
        remote_dashboard = "public_html/deploy_dashboard_update.php"
        print(f"Uploading {dashboard_php} to {remote_dashboard}...")
        bot.upload_file(dashboard_php, remote_dashboard)
        
        # Upload WordPress Template
        remote_template = "public_html/wp-content/themes/caviar-premium/page-client-status.php"
        print(f"Uploading {template_php} to {remote_template}...")
        bot.upload_file(template_php, remote_template)
        
        # Upload Layout Page Template (page.php)
        layout_php = r"c:\sandbox\esm\wp-content\themes\caviar-premium\page.php"
        remote_layout = "public_html/wp-content/themes/caviar-premium/page.php"
        print(f"Uploading {layout_php} to {remote_layout}...")
        bot.upload_file(layout_php, remote_layout)
        
        # Execute Dashboard Deployer
        deploy_url = "https://elliotspencermorgan.com/deploy_dashboard_update.php?key=antigravity_deploy_2025"
        print(f"Executing deployment script at {deploy_url}...")
        bot.visit(deploy_url)
        print("Deployment script executed.")
        
        print("Uploads completed successfully.")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
