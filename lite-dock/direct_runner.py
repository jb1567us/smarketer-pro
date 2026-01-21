import subprocess
import os
import sys
import time
import signal

def get_wsl_path(win_path):
    """Converts a Windows path to a WSL /mnt/c/... path."""
    # Simple conversion for C: drive
    if win_path[1:3] == ":\\":
        return "/mnt/" + win_path[0].lower() + win_path[2:].replace("\\", "/")
    return win_path.replace("\\", "/")

def run_searxng_direct():
    print("[DirectRunner] 🚀 Preparing Direct WSL Execution...")
    
    # 1. config paths
    user_profile = os.environ.get('USERPROFILE')
    image_base = os.path.join(user_profile, ".litedock", "images", "searxng_searxng_latest")
    
    if not os.path.exists(image_base):
        print(f"[DirectRunner] ❌ Image path not found: {image_base}")
        return

    # WSL Paths
    wsl_image_base = get_wsl_path(image_base)
    
    # Paths derived from the image structure
    # The image has a venv at /usr/local/searxng/.venv
    # We need to add its site-packages to PYTHONPATH
    
    # Note: We will use the HOST's python (Alpine's python) to run the code
    # This avoids binary incompatibility issues with the image's python executable
    
    site_packages = f"{wsl_image_base}/usr/local/searxng/.venv/lib/python3.14/site-packages"
    # Fallback for python version if 3.14 doesn't exist (check 3.12, 3.11 etc)
    # Actually, let's check windows side what version the venv is
    venv_lib = os.path.join(image_base, "usr", "local", "searxng", ".venv", "lib")
    py_ver = "python3.14" # default expectation
    if os.path.exists(venv_lib):
        dirs = os.listdir(venv_lib)
        for d in dirs:
            if d.startswith("python"):
                py_ver = d
                break
    
    site_packages = f"{wsl_image_base}/usr/local/searxng/.venv/lib/{py_ver}/site-packages"
    searx_code = f"{wsl_image_base}/usr/local/searxng" # Base dir for imports?
    
    print(f"[DirectRunner] Detected Python path: {py_ver}")
    print(f"[DirectRunner] Site Packages: {site_packages}")
    
    # 2. Install Python in Sidecar if missing
    print("[DirectRunner] Ensuring Python & Dependencies exist in Sidecar...")
    # We explicitly install msgspec, uvloop, and lxml in the host to ensure binary compatibility
    # Image binaries (NTFS/glibc mismatch) won't work in Alpine host
    subprocess.run(["wsl", "-d", "lite-dock-host", "apk", "add", "--no-cache", "python3", "py3-pip", "yaml-dev", "gcc", "musl-dev", "python3-dev", "py3-lxml", "py3-yaml"], check=False)
    
    # Install binary deps that fail if loaded from image
    print("[DirectRunner] Installing critical binary extensions in Sidecar...")
    subprocess.run(["wsl", "-d", "lite-dock-host", "pip3", "install", "msgspec", "uvloop", "--break-system-packages"], check=False)
    
    # CRITICAL: Delete incompatible libs from Image so Python uses the Host versions
    print("[DirectRunner] Pruning incompatible libraries from Image...")
    libs_to_prune = ["msgspec", "uvloop", "lxml", "fasttext"]
    # We need the windows path to delete them
    # site_packages was constructed with WSL path logic, let's reconstruct win path
    win_site_packages = os.path.join(image_base, "usr", "local", "searxng", ".venv", "lib", py_ver, "site-packages")
    
    import shutil
    for lib in libs_to_prune:
        lib_path = os.path.join(win_site_packages, lib)
        if os.path.exists(lib_path):
             print(f"   - Removing {lib} from image")
             try:
                 shutil.rmtree(lib_path)
             except Exception as e:
                 print(f"Failed to remove {lib}: {e}")

    # 3. Environment Variables
    # We put the Image's site-packages back in PYTHONPATH for pure-python deps
    # But now it won't have the broken binaries
    env_vars = {
        "PYTHONPATH": f"{wsl_image_base}/usr/local/searxng:{site_packages}",
        "SEARXNG_BASE_URL": "http://localhost:8081",
        "SEARXNG_PORT": "8081",  # Standardize on 8081 for compatibility with Docker config
        "SEARXNG_BIND_ADDRESS": "0.0.0.0",
        "SEARXNG_SETTINGS_PATH": f"{wsl_image_base}/usr/local/searxng/searx/settings.yml",
        "UWSGI_WORKERS": "1",
        "UWSGI_THREADS": "1"
    }
    
    env_str = " ".join([f"export {k}='{v}';" for k,v in env_vars.items()])
    
    # 4. Command
    # We run 'python3 -m searx.webapp' directly
    # check if granian is used or simple python run. The original command used granian.
    # granian might be a binary in bin.
    # Let's try running via python -m searx.webapp which is usually valid for flask apps
    
    cmd_str = f"{env_str} python3 -m searx.webapp"
    
    full_cmd = ["wsl", "-d", "lite-dock-host", "sh", "-c", cmd_str]
    
    print("[DirectRunner] Starting SearXNG...")
    print(f"[DirectRunner] Command: wsl -d lite-dock-host ... python3 -m searx.webapp")
    
    # Return the process object so auto_runner can manage it
    proc = subprocess.Popen(full_cmd)
    return proc

if __name__ == "__main__":
    p = run_searxng_direct()
    try:
        p.wait()
    except KeyboardInterrupt:
        p.terminate()
