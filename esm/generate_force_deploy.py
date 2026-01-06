import base64
import os

files = [
    {
        'local': r'c:\sandbox\esm\esm-trade-portal.php',
        'remotes': [
            '/home/elliotspencermor/public_html/content/plugins/esm-trade-portal/esm-trade-portal.php',
            '/home/elliotspencermor/public_html/wp-content/plugins/esm-trade-portal/esm-trade-portal.php'
        ]
    },
    {
        'local': r'c:\sandbox\esm\esm-trade-portal.js',
        'remotes': [
            '/home/elliotspencermor/public_html/content/plugins/esm-trade-portal/esm-trade-portal.js',
            '/home/elliotspencermor/public_html/wp-content/plugins/esm-trade-portal/esm-trade-portal.js'
        ]
    }
]

deploy_script_content = "<?php\n"
deploy_script_content += "echo '<pre>';\n"
deploy_script_content += "echo 'User: ' . get_current_user() . ' | UID: ' . getmyuid() . \"\\n\";\n"

for file in files:
    if not os.path.exists(file['local']):
        print(f"Missing local file: {file['local']}")
        exit(1)
        
    with open(file['local'], 'rb') as f:
        content = f.read()
    
    base64_content = base64.b64encode(content).decode('utf-8')
    
    deploy_script_content += f"\n// PROCESSING: {os.path.basename(file['local'])}\n"
    deploy_script_content += f"$content = base64_decode('{base64_content}');\n"
    
    for dest in file['remotes']:
        deploy_script_content += f"echo 'Target: {dest}' . \"\\n\";\n"
        deploy_script_content += f"if (file_exists('{dest}')) {{\n"
        deploy_script_content += f"    echo '  Existing Owner: ' . fileowner('{dest}') . \"\\n\";\n"
        deploy_script_content += f"    echo '  Writable: ' . (is_writable('{dest}') ? 'YES' : 'NO') . \"\\n\";\n"
        deploy_script_content += f"    // Try to chmod\n"
        deploy_script_content += f"    @chmod('{dest}', 0666);\n"
        deploy_script_content += f"}}\n"
        
        deploy_script_content += f"if (file_put_contents('{dest}', $content) !== false) {{\n"
        deploy_script_content += f"    echo '  SUCCESS: Updated.' . \"\\n\";\n"
        deploy_script_content += f"}} else {{\n"
        deploy_script_content += f"    echo '  ERROR: Write failed.' . \"\\n\";\n"
        deploy_script_content += f"    // Try unlink and write\n"
        deploy_script_content += f"    if (unlink('{dest}')) {{\n"
        deploy_script_content += f"        echo '  Deleted old file.' . \"\\n\";\n"
        deploy_script_content += f"        if (file_put_contents('{dest}', $content) !== false) echo '  SUCCESS: Wrote new file.' . \"\\n\";\n"
        deploy_script_content += f"        else echo '  FATAL: Could not write after delete.' . \"\\n\";\n"
        deploy_script_content += f"    }} else echo '  ERROR: Could not delete old file.' . \"\\n\";\n"
        deploy_script_content += f"}}\n"

deploy_script_content += "echo '</pre>';\n"

output_file = r'c:\sandbox\esm\prepare_force_deploy.php' # The generator, not the payload
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(deploy_script_content)

print(f"Generated generator at: {output_file}")
