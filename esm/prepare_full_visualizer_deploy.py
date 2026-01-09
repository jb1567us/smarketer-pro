import base64
import os

files = [
    {
        'local': r'c:\sandbox\esm\esm-trade-portal.php',
        'remote': '/home/elliotspencermor/public_html/content/plugins/esm-trade-portal/esm-trade-portal.php'
    },
    {
        'local': r'c:\sandbox\esm\esm-trade-portal.js',
        'remote': '/home/elliotspencermor/public_html/content/plugins/esm-trade-portal/esm-trade-portal.js'
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
    dest = file['remote']
    
    deploy_script_content += f"\n// Deploying to {dest}\n"
    deploy_script_content += f"$dest = '{dest}';\n"
    deploy_script_content += f"$content = base64_decode('{base64_content}');\n"
    deploy_script_content += "if (file_put_contents($dest, $content) !== false) {\n"
    deploy_script_content += "    echo 'Successfully updated: ' . $dest . \"\\n\";\n"
    deploy_script_content += "} else {\n"
    deploy_script_content += "    echo 'ERROR: Failed to write to ' . $dest . \"\\n\";\n"
    deploy_script_content += "}\n"

deploy_script_content += "echo '</pre>';\n"

output_file = r'c:\sandbox\esm\deploy_full_visualizer.php'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(deploy_script_content)

print(f"Generated deployment script at: {output_file}")
