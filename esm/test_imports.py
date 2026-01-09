import sys
import traceback

log_file = r"c:\sandbox\esm\import_log.txt"

with open(log_file, "w") as f:
    f.write("Start\n")
    try:
        sys.path.append(r"c:\sandbox\esm\webhost-automation")
        f.write("Path appended\n")
        
        import webhost_automation
        f.write("Imported webhost_automation package\n")
        
        from webhost_automation.config import Config
        f.write("Imported Config\n")
        
        from webhost_automation.browser_bot import BrowserBot
        f.write("Imported BrowserBot\n")
        
    except Exception:
        f.write("Import Error:\n")
        f.write(traceback.format_exc())
