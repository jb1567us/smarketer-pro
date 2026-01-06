import ftplib
import os

FTP_HOST = "ftp.lookoverhere.xyz"
FTP_USER = "lookoverhere"
FTP_PASS = "!Meimeialibe4r"
REMOTE_PATH = "/product_insights" # Uploading peer to public_html for security/Node standards

IGNORE_LIST = ['.git', 'node_modules', '_legacy_php_backup', '_legacy_nextjs_backup', '.next', 'list_ftp.py', 'deploy.py', '.env.example', '.venv', '__pycache__']

def upload_files(ftp, local_path, remote_path):
    if not os.path.exists(local_path):
        return

    print(f"Entering {remote_path}...")
    
    # Ensure remote dir exists
    try:
        ftp.mkd(remote_path)
        print(f"Created remote directory: {remote_path}")
    except ftplib.error_perm:
        pass # Directory likely exists

    ftp.cwd(remote_path)

    for item in os.listdir(local_path):
        if item in IGNORE_LIST:
            continue

        local_item_path = os.path.join(local_path, item)
        
        if os.path.isfile(local_item_path):
            print(f"Uploading {item}...")
            with open(local_item_path, 'rb') as f:
                ftp.storbinary(f'STOR {item}', f)
        elif os.path.isdir(local_item_path):
            upload_files(ftp, local_item_path, f"{remote_path}/{item}")
            # Return to parent after recursive call
            ftp.cwd(remote_path)

try:
    print(f"Connecting to {FTP_HOST}...")
    ftp = ftplib.FTP(FTP_HOST)
    ftp.login(FTP_USER, FTP_PASS)
    print("Login successful.")

    upload_files(ftp, ".", REMOTE_PATH)
    
    print("\nUpload Complete!")
    ftp.quit()
except Exception as e:
    print(f"\nError: {e}")
