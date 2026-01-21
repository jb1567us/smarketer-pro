import os
import urllib.request
import zipfile
import shutil
import sys

GO_VERSION = "1.23.0"
GO_URL = f"https://go.dev/dl/go{GO_VERSION}.windows-amd64.zip"
INSTALL_DIR = os.path.join(os.environ["USERPROFILE"], ".litedock", "go_toolchain_v2")
ZIP_PATH = os.path.join(INSTALL_DIR, "go.zip")

def install_go():
    if os.path.exists(os.path.join(INSTALL_DIR, "go", "bin", "go.exe")):
        print(f"Go already installed at {INSTALL_DIR}")
        return

    print(f"Creating directory {INSTALL_DIR}...")
    os.makedirs(INSTALL_DIR, exist_ok=True)

    print(f"Downloading Go {GO_VERSION} from {GO_URL}...")
    try:
        urllib.request.urlretrieve(GO_URL, ZIP_PATH)
    except Exception as e:
        print(f"Download failed: {e}")
        return

    print("Extracting zip file...")
    try:
        with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
            zip_ref.extractall(INSTALL_DIR)
    except Exception as e:
        print(f"Extraction failed: {e}")
        return
    
    # Cleanup
    try:
        os.remove(ZIP_PATH)
    except:
        pass

    print("Go installation complete.")
    print(f"Go binary is at: {os.path.join(INSTALL_DIR, 'go', 'bin', 'go.exe')}")

if __name__ == "__main__":
    install_go()
