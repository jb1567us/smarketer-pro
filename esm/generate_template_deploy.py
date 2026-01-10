import base64
import os

def create_deployment_php():
    files_to_deploy = [
        {
            "local": r"c:\sandbox\esm\esm-artwork-template.php",
            "remote": "esm-artwork-template.php" 
        },
        {
            "local": r"c:\sandbox\esm\esm-artwork-template_NEW.php",
            "remote": "esm-artwork-template_NEW.php"
        },
        {
            "local": r"c:\sandbox\esm\esm-template-v3.php",
            "remote": "esm-template-v3.php"
        },
        {
            "local": r"c:\sandbox\esm\wp-content\themes\caviar-premium\page.php",
            "remote": "wp-content/themes/caviar-premium/page.php"
        }
    ]
    
    output_php = r'c:\sandbox\esm\deploy_templates_fix.php'
    
    php_content_parts = []
    
    # Header
    php_content_parts.append("<?php")
    php_content_parts.append("// deploy_templates_fix.php")
    php_content_parts.append("// Deploys updated templates to fix spec sheet links (Slug Logic)")
    php_content_parts.append("header('Content-Type: text/plain');")
    php_content_parts.append("echo \"Starting Template Deployment...\\n\";")
    php_content_parts.append("$base_dir = $_SERVER['DOCUMENT_ROOT'];")
    
    for item in files_to_deploy:
        try:
            with open(item['local'], 'rb') as f:
                b64 = base64.b64encode(f.read()).decode('utf-8')
                
            remote_path_var = item['remote'].replace('/', '_').replace('.', '_').replace('-', '_')
            
            php_content_parts.append(f"// Deploying {item['remote']}")
            php_content_parts.append(f"${remote_path_var}_b64 = '{b64}';")
            php_content_parts.append(f"$target_{remote_path_var} = $base_dir . '/{item['remote']}';")
            
            # Ensure directory exists for nested files
            if '/' in item['remote']:
                dir_name = os.path.dirname(item['remote'])
                php_content_parts.append(f"if (!file_exists($base_dir . '/{dir_name}')) {{ mkdir($base_dir . '/{dir_name}', 0755, true); }}")

            php_content_parts.append(f"if (file_put_contents($target_{remote_path_var}, base64_decode(${remote_path_var}_b64))) {{")
            php_content_parts.append(f"    echo \"SUCCESS: Updated {item['remote']}\\n\";")
            php_content_parts.append("} else {")
            php_content_parts.append(f"    echo \"ERROR: Failed to update {item['remote']}\\n\";")
            php_content_parts.append("}")
            php_content_parts.append("")
            
        except Exception as e:
            print(f"Error reading {item['local']}: {e}")
            return

    php_content_parts.append("echo \"Deployment Complete.\\n\";")
    php_content_parts.append("?>")

    with open(output_php, 'w', encoding='utf-8') as f:
        f.write("\n".join(php_content_parts))
    
    print(f"Generated {output_php}")

if __name__ == "__main__":
    create_deployment_php()
