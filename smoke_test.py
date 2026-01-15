
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

print("Testing imports...")

try:
    import src.app
    print("✅ src.app imported successfully")
except Exception as e:
    print(f"❌ src.app import failed: {e}")

try:
    import src.workflow
    print("✅ src.workflow imported successfully")
except Exception as e:
    print(f"❌ src.workflow import failed: {e}")

try:
    import src.agents.researcher
    print("✅ src.agents.researcher imported successfully")
except Exception as e:
    print(f"❌ src.agents.researcher import failed: {e}")

print("Smoke test complete.")
