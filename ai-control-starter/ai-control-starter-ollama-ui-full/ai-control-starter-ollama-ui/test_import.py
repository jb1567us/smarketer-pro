import sys
from pathlib import Path

# Add parent directory to path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

print("Python path:")
for path in sys.path:
    print(f"  {path}")

try:
    import model_client
    print("✓ SUCCESS: model_client imported successfully!")
    
    # Test a simple function
    from model_client import load_config
    config = load_config()
    print(f"✓ Config loaded: {config.get('backend')}")
    
except ImportError as e:
    print(f"✗ FAILED: {e}")