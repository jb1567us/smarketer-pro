import os
import zipfile

def zip_directory(folder_path, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)
                print(f"Added: {arcname}")

if __name__ == "__main__":
    src = r"c:\sandbox\esm\spec_sheets_v3"
    dst = r"c:\sandbox\esm\spec_sheets_v3.zip"
    zip_directory(src, dst)
    print("Zip complete.")
