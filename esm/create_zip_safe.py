import zipfile
import os

source_dir = r"c:\sandbox\esm\wp-content\themes\caviar-premium"
output_filename = r"c:\sandbox\esm\caviar-premium-v2.zip"

def zip_dir(path, ziph):
    # ziph is zipfile handle
    # root_folder_name = os.path.basename(path)
    root_folder_name = "caviar-premium"
    
    for root, dirs, files in os.walk(path):
        for file in files:
            abs_file = os.path.join(root, file)
            # Create relative path from the source_dir
            rel_path = os.path.relpath(abs_file, source_dir)
            # Prepend the root folder name to ensure it unzips into a folder
            zip_path = os.path.join(root_folder_name, rel_path)
            
            print(f"Adding {zip_path}...")
            ziph.write(abs_file, zip_path)

if __name__ == '__main__':
    zipf = zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED)
    zip_dir(source_dir, zipf)
    zipf.close()
    print(f"Created {output_filename}")
