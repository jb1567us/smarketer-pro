import os
import sys
import traceback

# Hardcoded absolute path for certainty
SRC_PATH = r"d:\sandbox\smarketer-pro\src"

log_file = os.path.join(os.path.dirname(__file__), 'stealth_log.txt')

def log(msg):
    with open(log_file, 'a') as f:
        f.write(msg + "\n")

if os.path.exists(log_file):
    os.remove(log_file)

log("Script started.")
log(f"Inserting {SRC_PATH} to sys.path at index 0")
sys.path.insert(0, SRC_PATH)

try:
    log("Importing asyncio...")
    import asyncio
    
    log("Importing BrowserManager...")
    # Try importing top level utils first
    import utils
    from utils.browser_manager import BrowserManager
    log("BrowserManager imported.")

    async def test_stealth():
        log("Initializing BrowserManager...")
        bm = BrowserManager(session_id="test_stealth")
        
        try:
            log("Launching browser...")
            page = await bm.launch(headless=True)
            log("Browser launched.")
            
            log("Checking Stealth Properties:")
            
            ua = await page.evaluate("navigator.userAgent")
            log(f"  User Agent: {ua}")
            
            vp = await page.evaluate("({w: window.innerWidth, h: window.innerHeight})")
            log(f"  Viewport: {vp['w']}x{vp['h']}")
            
            wd = await page.evaluate("navigator.webdriver")
            log(f"  navigator.webdriver: {wd}")
            
            if not wd:
                log("SUCCESS: navigator.webdriver is hidden!")
            else:
                log("FAILURE: navigator.webdriver is visible.")
                
        except Exception:
            log(f"Runtime Error: {traceback.format_exc()}")
        finally:
            log("Closing browser...")
            await bm.close()
            log("Closed.")

    if __name__ == "__main__":
        # if sys.platform == 'win32':
        #     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(test_stealth())
        
except Exception:
    log(f"CRITICAL ERROR: {traceback.format_exc()}")
