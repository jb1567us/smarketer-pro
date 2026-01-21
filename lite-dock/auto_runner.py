import subprocess
import time
import sys
import signal
import os
from inject_proxies import inject_proxies

# Config
ROTATION_INTERVAL_SECONDS = 1800 # Rotate every 30 minutes
CONTAINER_NAME = "searxng_debug"
IMAGE_NAME = "searxng/searxng:latest"

running_process = None

def signal_handler(sig, frame):
    print("\n[AutoRunner] Stopping...")
    if running_process:
        running_process.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def check_preflights():
    """Ensures lite-dock image is present and dependencies are met."""
    print("[AutoRunner] Running pre-flight checks...")
    
    # 1. Check if image exists
    # We check the directory structure expected by inject_proxies.py
    user_profile = os.environ.get('USERPROFILE')
    settings_path = os.path.join(user_profile, '.litedock', 'images', 'searxng_searxng_latest', 'usr', 'local', 'searxng', 'searx', 'settings.yml')
    
    if not os.path.exists(settings_path):
        print(f"[AutoRunner] Image {IMAGE_NAME} not found. Attempting to pull...")
        try:
            # Determine platform executable
            base_dir = os.path.dirname(os.path.abspath(__file__))
            exe = os.path.join(base_dir, "lite-dock.exe") if sys.platform == 'win32' else "./lite-dock"
            subprocess.run([exe, "pull", IMAGE_NAME], check=True)
            print("[AutoRunner] Image pulled successfully.")
        except Exception as e:
            print(f"[AutoRunner] ❌ Failed to pull image: {e}")
            return False

    # 2. Check for Sidecar Distro (lite-dock-host)
    # This acts as our 'kernel' and 'runtime' host for the container files
    try:
        # WSL output is often UTF-16-LE on Windows
        proc = subprocess.run(["wsl", "-l"], capture_output=True, check=True)
        try:
            wsl_list = proc.stdout.decode('utf-16-le')
        except:
            wsl_list = proc.stdout.decode('utf-8', errors='ignore')
            
        if "lite-dock-host" not in wsl_list:
            print("[AutoRunner] Sidecar distro 'lite-dock-host' not found. Installing...")
            
            # A. Download Alpine Mini RootFS
            alpine_url = "https://dl-cdn.alpinelinux.org/alpine/v3.19/releases/x86_64/alpine-minirootfs-3.19.1-x86_64.tar.gz"
            base_dir = os.path.dirname(os.path.abspath(__file__))
            host_distro_dir = os.path.join(user_profile, '.litedock', 'host-distro')
            tar_path = os.path.join(host_distro_dir, "alpine.tar.gz")
            
            os.makedirs(host_distro_dir, exist_ok=True)
            
            # Use curl (assuming available on Win10+) or python download
            if not os.path.exists(tar_path):
                 print(f"[AutoRunner] Downloading Alpine from {alpine_url}...")
                 # Simple python download
                 import urllib.request
                 urllib.request.urlretrieve(alpine_url, tar_path)
            
            # B. Import Distro
            print("[AutoRunner] Importing Sidecar Distro...")
            subprocess.run(["wsl", "--import", "lite-dock-host", host_distro_dir, tar_path, "--version", "2"], check=True)
            
            # C. Install runc
            print("[AutoRunner] Installing runc in Sidecar...")
            subprocess.run(["wsl", "-d", "lite-dock-host", "apk", "add", "runc"], check=True)
            
            print("[AutoRunner] Sidecar setup complete.")
    except Exception as e:
        print(f"[AutoRunner] ❌ Failed to setup Sidecar Distro: {e}")
        return False
        
    return True

def run_rotation_loop():
    global running_process
    
    if not check_preflights():
        print("[AutoRunner] ❌ Pre-flight checks failed. Aborting.")
        return

    print(f"[AutoRunner] Started. Rotation Interval: {ROTATION_INTERVAL_SECONDS/60:.0f} minutes.", flush=True)
    
    first_run = True
    consecutive_crashes = 0
    MAX_CRASHES = 3
    
    while True:
        print("\n[AutoRunner] >>> STARTING ROTATION CYCLE <<<", flush=True)
        
        # 1. Refresh Proxies
        # On first run, we use cache if available. Subsequest runs force refresh.
        start_time = time.time()
        success = inject_proxies(force_refresh=(not first_run))
        
        if not success and not first_run:
            print("[AutoRunner] Failed to refresh proxies. Keeping previous batch...")
        
        # 2. Start Lite-Dock (Direct Mode)
        print(f"[AutoRunner] Launching SearXNG via Direct WSL Runner...", flush=True)
        try:
            # Import dynamically to ensure we get latest if changed
            import direct_runner
            import importlib
            importlib.reload(direct_runner)
            
            # This launches the process and returns the Popen object
            running_process = direct_runner.run_searxng_direct()
            
            # 3. Wait Duration
            
            # 3. Wait Duration
            # We wait in small chunks to handle Ctrl+C responsively
            elapsed = 0
            while elapsed < ROTATION_INTERVAL_SECONDS:
                if running_process.poll() is not None:
                     print("[AutoRunner] Container process exited unexpectedly!")
                     break
                time.sleep(1)
                elapsed += 1
            
            # 4. Stop and cycle
            if running_process.poll() is None:
                print("[AutoRunner] Time's up! Rotating proxies...")
                running_process.terminate()
                try:
                    running_process.wait(timeout=10)
                except:
                    running_process.kill()
            
            running_process = None
            first_run = False
            
        except Exception as e:
            print(f"[AutoRunner] Error: {e}")
            time.sleep(5)

        # Fatal Error Check
        # logic handled within Popen block above where we print unexpected exit, 
        # but let's make it robust here.
        
        # Crash Loop Detection
        run_duration = time.time() - start_time
        # Increase threshold to 60s because failed hydration is slow
        if running_process is None or run_duration < 60:
             consecutive_crashes += 1
             print(f"[AutoRunner] ⚠️ Detected rapid crash ({consecutive_crashes}/{MAX_CRASHES}).")
        else:
             consecutive_crashes = 0
             
        if consecutive_crashes >= MAX_CRASHES:
            print("[AutoRunner] ❌ Too many consecutive crashes. Aborting.")
            # Check if we should fallback? start_app.bat handles fallback if we exit non-zero
            sys.exit(1)
            
if __name__ == "__main__":
    run_rotation_loop()
