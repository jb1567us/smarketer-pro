from ftplib import FTP
import os

# FTP Credentials
FTP_HOST = "ftp.elliotspencermorgan.com"
FTP_USER = "admin@elliotspencermorgan.com"
FTP_PASS = "!Meimeialibe4r"

def list_files():
    try:
        print(f"Connecting to {FTP_HOST}...")
        ftp = FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        print("✅ Login successful!")

        # Try to find the uploads directory
        # Standard cPanel/WP structure usually starts at public_html
        paths_to_try = [
             "/public_html/wp-content/uploads/2025/11",
             "/wp-content/uploads/2025/11",
             "/www/wp-content/uploads/2025/11",
             "/uploads/2025/11" 
        ]
        
        target_dir = None
        for path in paths_to_try:
            try:
                ftp.cwd(path)
                target_dir = path
                print(f"✅ Found directory: {path}")
                break
            except Exception as e:
                print(f"Directory not found: {path}")

        if not target_dir:
            print("❌ Could not locate specific directory. Exploring root...")
            
            # List current directory
            print(f"Current Path: {ftp.pwd()}")
            
            print("Listing files/dirs:")
            root_items = []
            ftp.retrlines('LIST', root_items.append)
            
            for item in root_items:
                print(item)
                
            # Try to guess - if we see an 'elliotspencermorgan.com' folder or 'public_html'
            return
        print("=============================")
        
        # Capture file listing
        files = []
        ftp.retrlines('NLST', files.append)
        
        # Filter for "Lake" to see the pattern
        lake_files = [f for f in files if "Lake" in f]
        portal_files = [f for f in files if "Portal" in f]
        
        print("\n--- Lake Files ---")
        for f in lake_files:
            print(f)
            
        print("\n--- Portal Files ---")
        for f in portal_files:
            print(f)
            
        print("\n=============================")
        ftp.quit()
        
    except Exception as e:
        print(f"❌ FTP Error: {e}")

if __name__ == "__main__":
    list_files()
