
import os
import requests
from ftplib import FTP

# FTP Credentials
FTP_HOST = "elk.lev3.com"
FTP_USER = "elliotspencermor"
FTP_PASS = "!Meimeialibe4r"

def upload_file(ftp, local_path, remote_path):
    with open(local_path, 'rb') as f:
        ftp.storbinary(f'STOR {remote_path}', f)
    print(f"Uploaded {local_path} to {remote_path}")

def run_remote_script(script_name):
    url = f"https://elliotspencermorgan.com/{script_name}"
    print(f"Requesting {url}...")
    try:
        response = requests.get(url)
        print("Response Code:", response.status_code)
        print("Response Body:", response.text)
    except Exception as e:
        print(f"Failed to request script: {e}")

def main():
    try:
        ftp = FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        
        # 1. Upload PHP script
        upload_file(ftp, r'c:\sandbox\esm\hide_artworks_remote.php', 'public_html/hide_artworks_remote.php')
        
        # 2. Run PHP script
        run_remote_script('hide_artworks_remote.php')
        
        # 3. Upload fixed JSON
        upload_file(ftp, r'c:\sandbox\esm\artwork_data.json', 'public_html/artwork_data.json')
        
        # 4. Cleanup PHP script
        ftp.delete('public_html/hide_artworks_remote.php')
        print("Deleted remote script.")
        
        ftp.quit()
        print("Orchestration complete.")

    except Exception as e:
        print(f"Orchestration failed: {e}")

if __name__ == "__main__":
    main()
