import json
import os

# Config
HTML_FILE = r'C:\sandbox\esm\client_dashboard.html'
JS_OUTPUT = r'C:\sandbox\esm\upload_dashboard.js'

def prepare_upload_script():
    if not os.path.exists(HTML_FILE):
        print(f"Error: {HTML_FILE} not found.")
        return

    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Create the JS script
    # We will use the HTML content as the page content.
    # We need to escape it properly for a JS string.
    
    # WordPress usually handles full HTML in content if you use the Custom HTML block or logic, 
    # but for simplicity via API, we just dump it as raw HTML string.
    # To ensure styles work, we usually keep them inline or in <style> blocks.
    # The existing HTML has <style> in head. We'll strip <html>, <head>, <body> tags 
    # but KEEP the <style> block and the body *contents*.

    # Simple extraction
    # Find style
    style_start = html_content.find('<style>')
    style_end = html_content.find('</style>') + 8
    style_block = html_content[style_start:style_end] if style_start > -1 else ""

    # Find body content
    body_start = html_content.find('<body>') + 6
    body_end = html_content.find('</body>')
    body_content = html_content[body_start:body_end] if body_start > -1 else html_content

    # Combine
    final_content = f"{style_block}\n<div class='dashboard-wrapper'>{body_content}</div>"
    
    # Escape for JS template string
    # We use JSON.stringify to safely encode the string
    json_content = json.dumps(final_content)

    js_code = f"""
// Upload Dashboard to WordPress
// Run this in your browser console on the logged-in WordPress site

(async function() {{
    console.log("Starting Dashboard Upload...");
    
    if (typeof wp === 'undefined' || !wp.apiFetch) {{
        console.error("wp.apiFetch not found! Are you in the WP Admin?");
        return;
    }}

    const pageTitle = "Project Status";
    const pageSlug = "project-status";
    const pageContent = {json_content};

    // 1. Check if page exists
    const existing = await wp.apiFetch({{ path: `/wp/v2/pages?slug=${{pageSlug}}&status=any` }});
    
    let result;
    if (existing.length > 0) {{
        const id = existing[0].id;
        console.log(`Updating existing page '${{pageTitle}}' (ID: ${{id}})...`);
        result = await wp.apiFetch({{
            path: `/wp/v2/pages/${{id}}`,
            method: 'POST',
            data: {{
                title: pageTitle,
                content: pageContent,
                status: 'private', // Keep private for client/admin only
                parent: 0 // Top Level
            }}
        }});
    }} else {{
        console.log(`Creating new page '${{pageTitle}}'...`);
        result = await wp.apiFetch({{
            path: '/wp/v2/pages',
            method: 'POST',
            data: {{
                title: pageTitle,
                slug: pageSlug,
                content: pageContent,
                status: 'private', // Keep private for client/admin only
                parent: 0 // Top Level
            }}
        }});
    }}

    console.log("SUCCESS! Dashboard uploaded.");
    console.log("View it here:", result.link);
    console.log("Edit it here:", `/wp-admin/post.php?post=${{result.id}}&action=edit`);
    alert(`Dashboard Uploaded Successfully!\\n\\nLink: ${{result.link}}`);
}})();
"""

    with open(JS_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(js_code)
    
    print(f"Generated {JS_OUTPUT}")

if __name__ == "__main__":
    prepare_upload_script()
