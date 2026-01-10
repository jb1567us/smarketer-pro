from webhost_automation.cli import get_client
from webhost_automation.file_manager import FileManager
import sys
import datetime

sys.path.append('.')

try:
    client = get_client()
    mgr = FileManager(client)
    
    files = mgr.list_files("public_html")
    found = False
    for f in files:
        if f.get("file") == "finalize_deployment.php":
            found = True
            mtime = f.get("mtime") # usually unix timestamp
            size = f.get("size")
            
            # formatting
            dt = datetime.datetime.fromtimestamp(int(mtime))
            print(f"File: {f.get('file')}")
            print(f"Size: {size}")
            print(f"MTime: {mtime} ({dt})")
            break
            
    if not found:
        print("File not found.")

except Exception as e:
    print(f"ERROR: {e}")
