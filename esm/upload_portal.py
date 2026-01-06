import sys
import os

# Add webhost-automation to path
sys.path.insert(0, r"c:\sandbox\esm\webhost-automation")

from webhost_automation.config import Config
from webhost_automation.browser_bot import BrowserBot

def log(msg):
    with open(r"c:\sandbox\esm\upload_debug.log", "a") as f:
        f.write(msg + "\n")
    print(msg)

def main():
    try:
        log("Starting upload_portal.py...")
        # Force load env from the correct directory
        os.chdir(r"c:\sandbox\esm\webhost-automation")
        log(f"CWD: {os.getcwd()}")
        
        # Explicitly load .env
        from dotenv import load_dotenv
        load_dotenv(".env")
        
        config = Config()
        try:
            config.validate()
            log("Config validated.")
        except Exception as e:
            log(f"Config validation failed: {e}")
            return

        # Initialize bot 
        log("Initializing BrowserBot...")
        bot = BrowserBot(config, headless=True) 
        
        local_file = r"c:\sandbox\esm\safe_writer.php"
        remote_path = "public_html/safe_writer.php"
        
        log(f"Starting upload of {local_file} to {remote_path}...")
        bot.upload_file(local_file, remote_path)
        log("Upload finished successfully.")
        
    except Exception as e:
        log(f"Error: {e}")
        import traceback
        log(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    # Clear log
    with open(r"c:\sandbox\esm\upload_debug.log", "w") as f:
        f.write("Log init\n")
    main()
