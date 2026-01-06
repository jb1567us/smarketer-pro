import base64
import os
import sys

try:
    source = r"c:\sandbox\esm\esm-trade-portal.php"
    with open(source, "rb") as f:
        data = f.read()
        
    b64 = base64.b64encode(data).decode('utf-8')
    
    # Try generic temp
    temp_dir = os.environ.get('TEMP') or os.environ.get('TMP') or r"C:\Windows\Temp"
    dest = os.path.join(temp_dir, 'portal_b64.txt')
    
    with open(dest, "w") as f:
        f.write(b64)
        
except Exception:
    pass
