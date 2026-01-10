import zipfile
import os

def create_zip():
    base_dir = r"c:\sandbox\esm"
    files = [
        "esm-deployment-fix.php",
        "artwork_data.json"
    ]
    zip_name = "deployment_package.zip"
    
    with zipfile.ZipFile(os.path.join(base_dir, zip_name), 'w') as zf:
        for file in files:
            zf.write(os.path.join(base_dir, file), arcname=file)
            print(f"Added {file}")
            
    print(f"Created {zip_name}")

if __name__ == "__main__":
    create_zip()
