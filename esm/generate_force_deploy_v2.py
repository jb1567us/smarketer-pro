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

for file in files:
    if not os.path.exists(file['local']):
        print(f"Missing local file: {file['local']}")
        exit(1)
        
    with open(file['local'], 'rb') as f:
        content = f.read()
    
    base64_content = base64.b64encode(content).decode('utf-8')
    md5_source = os.popen(f'certutil -hashfile "{file["local"]}" MD5').read().splitlines()[1].replace(' ', '').lower() # Window specific but works for me generating logic
    # Actually clearer to just php md5 it
    
    deploy_script_content += f"\n// PROCESSING: {os.path.basename(file['local'])}\n"
    deploy_script_content += f"$content = base64_decode('{base64_content}');\n"
    deploy_script_content += f"$source_md5 = md5($content);\n"
    deploy_script_content += f"echo 'Source MD5: ' . $source_md5 . \"\\n\";\n"
    
    for dest in file['remotes']:
        deploy_script_content += f"echo 'Target: {dest}' . \"\\n\";\n"
        
        # Unlink first
        deploy_script_content += f"if (file_exists('{dest}')) {{\n"
        deploy_script_content += f"    if (unlink('{dest}')) echo '  Deleted old file.' . \"\\n\";\n"
        deploy_script_content += f"    else echo '  WARNING: Could not delete.' . \"\\n\";\n"
        deploy_script_content += f"}}\n"
        
        # Write
        deploy_script_content += f"if (file_put_contents('{dest}', $content) !== false) {{\n"
        deploy_script_content += f"    echo '  Wrote bytes: ' . strlen($content) . \"\\n\";\n"
        
        # Verify
        deploy_script_content += f"    clearstatcache();\n"
        deploy_script_content += f"    $written_md5 = md5_file('{dest}');\n"
        deploy_script_content += f"    echo '  Written MD5: ' . $written_md5 . \"\\n\";\n"
        deploy_script_content += f"    if ($written_md5 === $source_md5) echo '  VERIFIED: Success.' . \"\\n\";\n"
        deploy_script_content += f"    else echo '  FATAL: Content mismatch.' . \"\\n\";\n"
        
        deploy_script_content += f"}} else {{\n"
        deploy_script_content += f"    echo '  ERROR: Write failed.' . \"\\n\";\n"
        deploy_script_content += f"}}\n"

deploy_script_content += "echo '</pre>';\n"

output_file = r'c:\sandbox\esm\prepare_force_deploy_v2.php'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(deploy_script_content)

print(f"Generated generator at: {output_file}")
