import subprocess
import os
import sys
import time
import psutil
from config import config

class LiteDockManager:
    """
    Manages the lifecycle of Lite-Dock as a fallback SearXNG provider.
    """
    def __init__(self):
        self.root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.litedock_dir = os.path.join(self.root_dir, "lite-dock")
        self.auto_runner_script = os.path.join(self.litedock_dir, "auto_runner.py")
        self.docker_available = None # Cache status

    def is_docker_running(self):
        """Checks if Docker daemon is responsive."""
        try:
            # Using 'docker info' is the standard way to check if daemon is running
            result = subprocess.run(["docker", "info"], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False

    def is_litedock_active(self):
        """Checks if the Lite-Dock auto_runner is already running."""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['cmdline'] and "auto_runner.py" in " ".join(proc.info['cmdline']):
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False

    def ensure_searxng(self):
        """
        Ensures a SearXNG instance is available.
        Prioritizes Docker, falls back to Lite-Dock if Docker is down.
        """
        if self.is_docker_running():
            print("[LiteDockManager] Docker is running. Standard SearXNG (Port 8081) prioritized.")
            return "docker"
        
        print("[LiteDockManager] 🚨 Docker is unavailable. Attempting Lite-Dock fallback...")
        
        if self.is_litedock_active():
            print("[LiteDockManager] Lite-Dock auto-runner is already active.")
            return "litedock"
        
        # Start Lite-Dock auto_runner in background
        try:
            # Run in a separate process group on windows to avoid killing it when main app exits if needed
            # For now, a simple background Popen is fine for persistent local dev
            subprocess.Popen(
                [sys.executable, self.auto_runner_script],
                cwd=self.litedock_dir,
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0,
                start_new_session=True
            )
            print("[LiteDockManager] 🚀 Lite-Dock auto-runner launched in a new console.")
            # Give it a tiny bit of time to start the proxy harvest and container
            # The user might need to wait a minute for full readiness, but we return control.
            return "litedock"
        except Exception as e:
            print(f"[LiteDockManager] ❌ Failed to launch Lite-Dock: {e}")
            return "none"

    def get_local_url(self):
        """Returns the appropriate local URL based on active management."""
        if self.is_docker_running():
            return config.get("search", {}).get("searxng_url", "http://localhost:8081/search")
        else:
            return "http://localhost:8080/search"

litedock_manager = LiteDockManager()
