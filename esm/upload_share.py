import sys
import os

# Add webhost-automation to path
sys.path.insert(0, r"c:\sandbox\esm\webhost-automation")

from webhost_automation.config import Config
from webhost_automation.browser_bot import BrowserBot

def main():
    try:
        # Force load env from the correct directory
        os.chdir(r"c:\sandbox\esm\webhost-automation")
        
        # Explicitly load .env
        from dotenv import load_dotenv
        load_dotenv(".env")
        
        config = Config()
        config.validate()

        # Initialize bot 
        print("Initializing BrowserBot...")
        bot = BrowserBot(config, headless=True) 
        
        local_file = r"c:\sandbox\esm\deploy_share_button.php"
        remote_path = "public_html/deploy_share_button.php"
        
        print(f"Starting upload of {local_file} to {remote_path}...")
        bot.upload_file(local_file, remote_path)
        print("Upload finished successfully.")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
