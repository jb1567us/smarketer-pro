from playwright.sync_api import sync_playwright
import time
import logging
from .config import HostingConfig

class BrowserBot:
    def __init__(self, config: HostingConfig, headless: bool = True):
        self.config = config
        self.headless = headless
        self.logger = logging.getLogger("hosting_browser")

    def run_backup(self):
        """Automates the 'Backup' -> 'Download a Full Account Backup' flow."""
        if not self.config.cpanel_password:
            raise ValueError("Browser automation requires CPANEL_PASSWORD.")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(ignore_https_errors=True)
            page = context.new_page()

            try:
                self.logger.info(f"Navigating to {self.config.cpanel_url}...")
                page.goto(self.config.cpanel_url)
                
                page.fill('input#user', self.config.cpanel_user)
                page.fill('input#pass', self.config.cpanel_password)
                page.click('button#login_submit')
                
                page.wait_for_load_state('networkidle')
                if "login" in page.url:
                    raise Exception("Login failed. Please check credentials.")
                
                self.logger.info("Login successful.")

                self.logger.info("Looking for Backup tool...")
                try:
                    page.fill('input#quick-jump-search', 'Backup')
                    page.press('input#quick-jump-search', 'Enter')
                except:
                    page.get_by_text("Backup", exact=True).first.click()

                page.wait_for_load_state('networkidle')

                self.logger.info("Initiating Full Backup...")
                page.get_by_role("link", name="Download a Full Account Backup").click()
                
                page.select_option('select[name="dest"]', 'homedir')
                
                try:
                    page.check('input[name="email_radio"][value="0"]') 
                except:
                    pass

                page.click('input[value="Generate Backup"]')
                
                page.wait_for_selector('text=Full Backup in Progress', timeout=10000)
                self.logger.info("Success: Full Backup is now in progress!")
                time.sleep(2)

            except Exception as e:
                self.logger.error(f"Browser Automation Failed: {e}")
                page.screenshot(path="hosting_error_screenshot.png")
                raise e
            finally:
                browser.close()
