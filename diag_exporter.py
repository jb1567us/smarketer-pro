import asyncio
import os
import sys

# Ensure backend is importable
sys.path.insert(0, os.getcwd())

from backend.reflex_exporter import export_static_site
from backend.database import DB_PATH

async def run_diag():
    print(f"DB_PATH: {DB_PATH}")
    print(f"DB Exists: {os.path.exists(DB_PATH)}")
    
    print("Running export_static_site()...")
    success = await export_static_site()
    print(f"Export Success: {success}")

if __name__ == "__main__":
    asyncio.run(run_diag())
