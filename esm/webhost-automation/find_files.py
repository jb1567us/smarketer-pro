from webhost_automation.cli import get_client
from webhost_automation.file_manager import FileManager
import sys

# Add current directory to sys.path
sys.path.append('.')

try:
    client = get_client()
    mgr = FileManager(client)
    files = mgr.list_files("public_html")
    
    found_files = []
    for f in files:
        if 'finalize_deployment' in f.get('file', ''):
            found_files.append(f.get('file'))
            
    print("MATCHES:", found_files)

except Exception as e:
    print(f"ERROR: {e}")
