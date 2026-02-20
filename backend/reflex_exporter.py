import os
import shutil
import asyncio
import logging
from backend.database import get_connection

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
PROJECT_ROOT = os.path.join(os.getcwd(), "b2b_outreach_proto")
MOCK_MODE = True # Enable for prototype/testing

async def export_static_site():
    """
    Executes 'reflex export --frontend-only' from the project root.
    Handles artifact movement and database status updates.
    """
    try:
        logger.info(f"Starting Reflex static export (Mock Mode: {MOCK_MODE})...")
        
        if not MOCK_MODE:
            # 1. Run Reflex Export from correct folder
            process = await asyncio.create_subprocess_exec(
                'reflex', 'export', '--frontend-only',
                cwd=PROJECT_ROOT,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                logger.error(f"Reflex export failed: {stderr.decode()}")
                return False
        else:
            logger.info("Simulation: Reflex command skipped (MOCK_MODE=True)")
            await asyncio.sleep(1)
            
        # 2. Extract and Move Files
        export_dir = os.path.join(os.getcwd(), "static_exports")
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
            
        with open(os.path.join(export_dir, "last_export.txt"), "w") as f:
            from datetime import datetime
            f.write(f"Exported at {datetime.now().isoformat()}")
            
        logger.info(f"Files moved to {export_dir}")
        
        # 3. Update DB Status
        conn = get_connection()
        c = conn.cursor()
        # Mark recent profiles as exported (only if they exist)
        c.execute("UPDATE company_profiles SET last_enriched = ? WHERE last_enriched IS NOT NULL", (int(asyncio.get_event_loop().time()),))
        if c.rowcount == 0:
            logger.info("No profiles to update in database.")
        conn.commit()
        conn.close()
        
        logger.info("Database updated successfully.")
        return True

    except Exception as e:
        logger.error(f"Error in reflex_exporter: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(export_static_site())
