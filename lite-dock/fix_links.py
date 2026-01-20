import os
import shutil

def fix_links():
    user_home = os.path.expanduser("~")
    image_base = os.path.join(user_home, ".litedock", "images", "searxng_searxng_latest")
    
    if not os.path.exists(image_base):
        print(f"Image base not found: {image_base}")
        return

    # Common symlinks in SearXNG image that fail on Windows
    # (Source path relative to image_base, Target path relative to symlink location)
    links_to_fix = [
        ("usr/bin/python", "python3.14"), # Usually python3.14 exists as a real file
        ("usr/bin/python3", "python3.14"),
        ("bin/sh", "busybox"),
        ("bin/bash", "busybox"), # Alpine often uses busybox for bash too
        ("usr/local/searxng/.venv/bin/python", "../../../../usr/bin/python3.14"),
        ("usr/local/searxng/.venv/bin/python3", "python"),
    ]

    for rel_path, target_rel in links_to_fix:
        symlink_path = os.path.join(image_base, rel_path.replace("/", os.sep))
        
        # If the symlink doesn't exist or is a 0-byte placeholder
        if not os.path.exists(symlink_path) or os.path.getsize(symlink_path) == 0:
            # Resolve target
            symlink_dir = os.path.dirname(symlink_path)
            target_path = os.path.normpath(os.path.join(symlink_dir, target_rel.replace("/", os.sep)))
            
            if os.path.exists(target_path) and not os.path.isdir(target_path):
                print(f"Fixing {rel_path} -> {target_rel} (Copying {target_path})")
                try:
                    os.makedirs(symlink_dir, exist_ok=True)
                    if os.path.exists(symlink_path): os.remove(symlink_path)
                    shutil.copy2(target_path, symlink_path)
                except Exception as e:
                    print(f"  Error fixing {rel_path}: {e}")
            else:
                # If target is missing, it might be deeper. We try to find a real python3.14
                real_python = os.path.join(image_base, "usr", "bin", "python3.14")
                if "python" in rel_path and os.path.exists(real_python):
                     print(f"Fixing {rel_path} using fallback {real_python}")
                     if os.path.exists(symlink_path): os.remove(symlink_path)
                     shutil.copy2(real_python, symlink_path)

    print("Symlink fix-up complete.")

if __name__ == "__main__":
    fix_links()
