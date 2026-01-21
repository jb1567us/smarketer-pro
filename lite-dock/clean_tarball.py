import tarfile
import os

def clean_tarball():
    print("--- Cleaning Corrupt Entries from Tarball ---")
    
    user_profile = os.environ.get('USERPROFILE')
    base_dir = os.path.join(user_profile, ".litedock", "images")
    src_path = os.path.join(base_dir, "searxng_searxng_latest.tar")
    dest_path = os.path.join(base_dir, "searxng_searxng_latest.clean.tar")
    
    if not os.path.exists(src_path):
        print(f"❌ Source tarball not found: {src_path}")
        return

    print(f"Source: {src_path}")
    print(f"Temp Output: {dest_path}")
    
    removed_count = 0
    
    try:
        # Open source for reading, new file for writing
        with tarfile.open(src_path, "r") as source_tar:
            with tarfile.open(dest_path, "w") as dest_tar:
                for member in source_tar:
                    # Filter condition
                    if "POSIX_V6_LP64_OFF64" in member.name:
                        print(f"🗑️  Removing bad entry: {member.name}")
                        removed_count += 1
                        continue
                    
                    # Copy valid member
                    if member.isfile():
                        f = source_tar.extractfile(member)
                        dest_tar.addfile(member, f)
                    else:
                        dest_tar.addfile(member)
                        
    except Exception as e:
        print(f"❌ Error during cleaning: {e}")
        if os.path.exists(dest_path):
            os.remove(dest_path)
        return

    print(f"Cleaning complete. Removed {removed_count} items.")
    
    if removed_count > 0:
        print("Swapping files...")
        backup_path = src_path + ".bak"
        if os.path.exists(backup_path): os.remove(backup_path)
        os.rename(src_path, backup_path)
        os.rename(dest_path, src_path)
        print("✅ Tarball patched! You can now run the launcher.")
    else:
        print("⚠️ No bad entries found. The file might already be clean.")
        if os.path.exists(dest_path): os.remove(dest_path)

if __name__ == "__main__":
    clean_tarball()
