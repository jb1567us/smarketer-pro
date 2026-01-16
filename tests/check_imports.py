import sys
import os
import asyncio

log_file = os.path.join(os.path.dirname(__file__), 'debug_log.txt')

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

with open(log_file, 'w') as f:
    f.write("Starting import check...\n")
    try:
        import fake_useragent
        f.write(f"fake_useragent version: {fake_useragent.__version__}\n")
        
        from fake_useragent import UserAgent
        ua = UserAgent()
        f.write(f"Random UA: {ua.random}\n")
        
        import playwright_stealth
        f.write("playwright_stealth imported successfully\n")
        
        from playwright_stealth import Stealth
        stealth = Stealth()
        f.write("Stealth class instantiated successfully\n")
        
        f.write("ALL CHECKS PASSED\n")
        
    except ImportError as e:
        f.write(f"IMPORT ERROR: {e}\n")
    except Exception as e:
        f.write(f"GENERAL ERROR: {e}\n")
