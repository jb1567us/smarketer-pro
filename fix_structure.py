import os
import shutil

BASE_DIR = r"d:\sandbox\smarketer-pro\lite-dock"
TARGET_DIR = os.path.join(BASE_DIR, "internal")

GROUPS = ["cli", "runtime", "image"]

def fix_structure():
    if not os.path.exists(TARGET_DIR):
        print(f"Creating {TARGET_DIR}...")
        os.makedirs(TARGET_DIR)

    for item in GROUPS:
        src = os.path.join(BASE_DIR, item)
        dst = os.path.join(TARGET_DIR, item)
        
        if os.path.exists(src):
            print(f"Moving {src} -> {dst}")
            try:
                shutil.move(src, dst)
            except Exception as e:
                print(f"Error moving {src}: {e}")
        else:
            print(f"Skipping {src} (not found or already moved)")

if __name__ == "__main__":
    fix_structure()
