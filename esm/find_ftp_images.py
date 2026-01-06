from ftplib import FTP

# FTP Credentials
FTP_HOST = "ftp.elliotspencermorgan.com"
FTP_USER = "admin@elliotspencermorgan.com"
FTP_PASS = "!Meimeialibe4r"

def find_images():
    try:
        print(f"Connecting to {FTP_HOST}...")
        ftp = FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        print("✅ Login successful!")

        # Helper to list files in a dir
        def get_files(path):
            files = []
            try:
                ftp.cwd(path)
                ftp.retrlines('NLST', files.append)
            except:
                pass
            return files

        # Recursive search (shallow for now)
        search_roots = ["/", "/public_html", "/elliotspencermorgan.com", "/www"]
        
        found_path = None
        
        for root in search_roots:
            print(f"Checking root: {root}")
            files = get_files(root)
            
            # Check if this looks like a WP root
            if "wp-content" in files:
                print(f"  Found wp-content in {root}")
                # Go deeper
                wp_path = f"{root}/wp-content/uploads"
                path_2025 = f"{wp_path}/2025/11"
                
                # Try to list 2025/11 directly
                print(f"  Checking {path_2025}...")
                upload_files = []
                try:
                    ftp.cwd(path_2025)
                    ftp.retrlines('NLST', upload_files.append)
                    print(f"  ✅ LISTING SUCCESS! Found {len(upload_files)} files.")
                    
                    print("\n--- SAMPLE FILES ---")
                    for f in upload_files:
                        if "Lake" in f or "Portal" in f:
                            print(f"  FILE: {f}")
                    return 
                    
                except Exception as e:
                    print(f"  Could not access {path_2025}: {e}")

        ftp.quit()
        
    except Exception as e:
        print(f"❌ FTP Error: {e}")

if __name__ == "__main__":
    find_images()
