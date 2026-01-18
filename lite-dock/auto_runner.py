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

def run_rotation_loop():
    global running_process
    
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
        cmd = [
            "lite-dock.exe", "run",
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
