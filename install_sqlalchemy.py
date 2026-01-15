import subprocess
import sys

try:
    print("Starting install...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "sqlalchemy"])
    print("Install complete.")
    with open("install_log.txt", "w") as f:
        f.write("SUCCESS")
except Exception as e:
    print(f"Error: {e}")
    with open("install_log.txt", "w") as f:
        f.write(f"FAILED: {e}")
