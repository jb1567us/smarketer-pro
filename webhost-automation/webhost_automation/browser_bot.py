from playwright.sync_api import sync_playwright
import time
from .config import Config

class BrowserBot:
    def __init__(self, config: Config, headless: bool = False):
        self.config = config
        self.headless = headless

    def run_backup(self):
        """
        Automates the 'Backup' -> 'Download a Full Account Backup' flow.
        """
        if not self.config.cpanel_password:
            raise ValueError("Browser automation requires CPANEL_PASSWORD.")

        with sync_playwright() as p:
            # Launch browser
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(ignore_https_errors=True) # cPanel often has self-signed certs
            page = context.new_page()

            try:
                # 1. Login
                print(f"Navigating to {self.config.cpanel_url}...")
                page.goto(self.config.cpanel_url)
                
                # Check if we are redirected to login
                # Selectors for cPanel login (standard themes)
                page.fill('input#user', self.config.cpanel_user)
                page.fill('input#pass', self.config.cpanel_password)
                page.click('button#login_submit')
                
                # Wait for dashboard
                page.wait_for_load_state('networkidle')
                if "login" in page.url:
                    raise Exception("Login failed. Please check credentials.")
                
                print("Login successful.")

                # 2. Search for Backup Wizard or Backup
                # We'll try to go directly to the backup page if possible, or search
                # Standard URL for backup: /frontend/paper_lantern/backup/index.html
                # But it varies by theme (jupiter, paper_lantern).
                # Safest is to use the search bar or text link.
                
                print("Looking for Backup tool...")
                # Search bar strategy is robust across themes
                try:
                    page.fill('input#quick-jump-search', 'Backup')
                    # Click the first result that looks like 'Backup' or 'Backup Wizard'
                    # Usually hitting enter works or waiting for dropdown
                    page.press('input#quick-jump-search', 'Enter')
                except:
                    # Fallback: look for link with text "Backup"
                    page.get_by_text("Backup", exact=True).first.click()

                page.wait_for_load_state('networkidle')

                # 3. Inside Backup Interface
                # We want "Download a Full Account Backup"
                # Often a button or link: "Download a Full Account Backup"
                print("Initiating Full Backup...")
                page.get_by_role("link", name="Download a Full Account Backup").click()
                
                # 4. Form configuration
                # Select Destination: Home Directory 
                # Selector often: select[name="dest"]
                page.select_option('select[name="dest"]', 'homedir')
                
                # Input email (optional), usually we select "Do not send email"
                # radio button: inputs[name="email_radio"][value="0"]
                try:
                    page.check('input[name="email_radio"][value="0"]') 
                except:
                    pass # Might not be present or different ID

                # 5. Submit
                page.click('input[value="Generate Backup"]')
                
                # 6. Verify success message
                # "Full Backup in Progress"
                page.wait_for_selector('text=Full Backup in Progress', timeout=10000)
                print("Success: Full Backup is now in progress!")
                
                # Sleep briefly to visualize if not headless
                time.sleep(2)

            except Exception as e:
                print(f"Browser Automation Failed: {e}")
                # Take screenshot for debug
                page.screenshot(path="error_screenshot.png")
                raise e
            finally:
                browser.close()

    def open_file_manager(self):
        """
        Navigates to the File Manager and keeps the browser open for the user.
        """
        if not self.config.cpanel_password:
            raise ValueError("Browser automation requires CPANEL_PASSWORD.")

        # For this interactive mode, we usually want headless=False
        if self.headless:
            print("Warning: Opening File Manager in headless mode might not be useful.")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()

            try:
                # Login Logic (Repeated - normally we'd refactor this into a private _login method)
                print(f"Navigating to {self.config.cpanel_url}...")
                page.goto(self.config.cpanel_url)
                
                page.fill('input#user', self.config.cpanel_user)
                page.fill('input#pass', self.config.cpanel_password)
                page.click('button#login_submit')
                page.wait_for_load_state('networkidle')
                
                print("Login successful. Navigating to File Manager...")

                # Go to File Manager
                try:
                    # Common direct link ID
                    page.click('#item_file_manager') 
                except:
                    # Fallback search
                    page.fill('input#quick-jump-search', 'File Manager')
                    page.press('input#quick-jump-search', 'Enter')
                
                print("File Manager opened! Press Ctrl+C in terminal to stop (or close browser).")
                
                # Keep alive loop
                while True:
                    time.sleep(1)
                    if page.is_closed():
                        break
                        
            except KeyboardInterrupt:
                print("\nExiting...")
            except Exception as e:
                print(f"Browser Error: {e}")
            finally:
                browser.close()

