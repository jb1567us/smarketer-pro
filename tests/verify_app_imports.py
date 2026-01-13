import sys
import os

# Mimic app.py path setup + Streamlit default behavior
current_dir = os.path.dirname(os.path.abspath(__file__)) # tests/
project_root = os.path.dirname(current_dir) # c:/sandbox/...
src_dir = os.path.join(project_root, 'src')

# Streamlit adds the script directory (src) to path
if src_dir not in sys.path:
    sys.path.append(src_dir)

# My fix adds the project root to path
if project_root not in sys.path:
    sys.path.append(project_root)

print(f"Project Root: {project_root}")
print(f"Src Dir: {src_dir}")
print(f"Sys Path: {sys.path}")

try:
    # Try importing the problematic module
    print("Attempting to import src.ui.manager_ui...")
    import src.ui.manager_ui
    print("SUCCESS: Imported src.ui.manager_ui")
except ImportError as e:
    print(f"FAILED: {e}")
    exit(1)
except Exception as e:
    print(f"FAILED with error: {e}")
    exit(1)
