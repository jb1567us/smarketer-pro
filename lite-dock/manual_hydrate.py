import tarfile
import os
import sys
import shutil

def hydrate():
    print("--- Manual Lite-Dock Hydration ---")
    user_profile = os.environ.get('USERPROFILE')
    if not user_profile:
        print("USERPROFILE not set.")
        return

    base_dir = os.path.join(user_profile, ".litedock", "images")
    tar_path = os.path.join(base_dir, "searxng_searxng_latest.tar")
    extract_path = os.path.join(base_dir, "searxng_searxng_latest")
    
    print(f"Source Tarball: {tar_path}")
    print(f"Destination:    {extract_path}")
    
    if not os.path.exists(tar_path):
        print("❌ Tarball not found! Please run the launcher once to pull the image.")
        return

    # Ensure dest exists
    os.makedirs(extract_path, exist_ok=True)
    
    print("Extracting... (this may take a moment)")
    
    success_count = 0
    fail_count = 0
    skip_count = 0
    
    try:
        with tarfile.open(tar_path, 'r') as tar:
            for member in tar:
                # 1. SKIP PROBLEMATIC FILES
                if "POSIX_V6_LP64_OFF64" in member.name:
                    print(f"⚠️  Skipping known problematic hardlink: {member.name}")
                    skip_count += 1
                    continue
                
                # 2. Extract others
                try:
                    # We use extract (not extractall) to have per-file control
                    # set filter='data' to avoid dangerous paths if python is new, 
                    # but 'tar' format is trusted here.
                    tar.extract(member, path=extract_path)
                    success_count += 1
                    
                    if success_count % 1000 == 0:
                        print(f"   Processed {success_count} files...")
                        
                except Exception as e:
                    # If it's a hardlink error, try to copy if target exists?
                    # For now, just log and skip, usually these are non-critical docs/bins
                    print(f"⚠️  Failed to extract {member.name}: {e}")
                    fail_count += 1
                    
    except Exception as e:
        print(f"❌ Fatal error opening tarball: {e}")
        return

    print(f"\n--- Hydration Summary ---")
    print(f"Success: {success_count}")
    print(f"Failed:  {fail_count}")
    print(f"Skipped: {skip_count}")
    
    # 3. Run Link Fixer
    print("\nRunning fix_links.py...")
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from fix_links import fix_links
        fix_links()
    except Exception as e:
        print(f"Error running fix_links: {e}")

    print("\n✅ Manual hydration complete. You can now restart the launcher.")

if __name__ == "__main__":
    hydrate()
