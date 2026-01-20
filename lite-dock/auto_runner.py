import subprocess
import time
import sys
import signal
import os
from inject_proxies import inject_proxies

# Config
ROTATION_INTERVAL_SECONDS = 1800 # Rotate every 30 minutes
CONTAINER_NAME = "searxng_debug"
IMAGE_NAME = "searxng/searxng"

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
            exe = "lite-dock.exe" if sys.platform == 'win32' else "./lite-dock"
            subprocess.run([exe, "pull", IMAGE_NAME], check=True)
            print("[AutoRunner] Image pulled successfully.")
        except Exception as e:
            print(f"[AutoRunner] ❌ Failed to pull image: {e}")
            return False

    # 2. Check for runc in WSL (Critical for Windows)
    if sys.platform == 'win32':
        try:
            res = subprocess.run(["wsl", "which", "runc"], capture_output=True, text=True)
            if res.returncode != 0:
                print("[AutoRunner] ⚠️ 'runc' not found in default WSL distribution.")
                print("[AutoRunner] Attempting to install 'runc' in WSL (requires sudo)...")
                # This might fail if no apt-get, but it's our best shot at auto-healing
                subprocess.run(["wsl", "-u", "root", "apt-get", "update"], capture_output=True)
                subprocess.run(["wsl", "-u", "root", "apt-get", "install", "-y", "runc"], capture_output=True)
                
                # Re-check
                res = subprocess.run(["wsl", "which", "runc"], capture_output=True, text=True)
                if res.returncode != 0:
                    print("[AutoRunner] ❌ Could not auto-install 'runc' in WSL.")
                    print("[AutoRunner] Please run: wsl -u root apt-get install runc")
                    return False
            print("[AutoRunner] ✅ 'runc' is available in WSL.")
        except Exception as e:
            print(f"[AutoRunner] Error checking WSL dependencies: {e}")
            return False
            
    return True

def run_rotation_loop():
    global running_process
    
    if not check_preflights():
        print("[AutoRunner] ❌ Pre-flight checks failed. Aborting.")
        return

    print(f"[AutoRunner] Started. Rotation Interval: {ROTATION_INTERVAL_SECONDS/60:.0f} minutes.")
    
    first_run = True
    
    while True:
        print("\n[AutoRunner] >>> STARTING ROTATION CYCLE <<<")
        
        # 1. Refresh Proxies
        # On first run, we use cache if available. Subsequest runs force refresh.
        start_time = time.time()
        success = inject_proxies(force_refresh=(not first_run))
        
        if not success and not first_run:
            print("[AutoRunner] Failed to refresh proxies. Keeping previous batch...")
        
        # 2. Start Lite-Dock
        # We construct the command manually to match run_searxng.bat
        exe = "lite-dock.exe" if sys.platform == 'win32' else "./lite-dock"
        cmd = [
            exe, "run",
            "--name", CONTAINER_NAME,
            "--network", "host",
            "-e", "SEARXNG_BASE_URL=http://localhost:8080",
            "-e", "SEARXNG_VERSION=0.0.0",
            "-e", "CONFIG_PATH=/usr/local/searxng/searx",
            "-e", "DATA_PATH=/usr/local/searxng/searx",
            "-e", "SEARXNG_SETTINGS_PATH=/usr/local/searxng/searx/settings.yml",
            IMAGE_NAME,
            "--", "sh", "-c", 
            "export PYTHONPATH=/usr/local/searxng/.venv/lib/python3.14/site-packages; " + 
            "/usr/bin/python3 /usr/local/searxng/.venv/bin/granian --interface wsgi --host 0.0.0.0 --port 8080 searx.webapp:app > /usr/local/searxng/debug.log 2>&1"
        ]
        
        print(f"[AutoRunner] Launching Lite-Dock...")
        try:
            running_process = subprocess.Popen(cmd)
            
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

if __name__ == "__main__":
    run_rotation_loop()
