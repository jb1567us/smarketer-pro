from webhost_automation.cli import get_client
from webhost_automation.file_manager import FileManager
import sys

sys.path.append('.')

try:
    client = get_client()
    mgr = FileManager(client)
    
    # This should now work with the patch
    res = mgr.get_file_content("public_html/finalize_deployment.php")
    content = res.get("content") if isinstance(res, dict) else res
    
    if content:
        print(f"Content Length: {len(content)}")
        print("Header Preview:")
        print(content[:200])
    else:
        print("No content retrieved.")

except Exception as e:
    print(f"ERROR: {e}")
