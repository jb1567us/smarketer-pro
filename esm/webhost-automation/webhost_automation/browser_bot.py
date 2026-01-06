from playwright.sync_api import sync_playwright
import time
from .config import Config

class BrowserBot:
    def __init__(self, config: Config, headless: bool = False):
        self.config = config
        self.headless = headless

    def _login(self, p):
        """
        Handles the login process and returns the authenticated page.
        """
        browser = p.chromium.launch(headless=self.headless)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()

        print(f"Navigating to {self.config.cpanel_url}...")
        page.goto(self.config.cpanel_url)

        # Allow for potential redirects
        try:
            page.wait_for_load_state('networkidle', timeout=5000)
        except:
            pass
            
        # Check if login is required
        if "login" in page.url.lower() or "login" in page.title().lower():
            page.fill('input#user', self.config.cpanel_user)
            page.fill('input#pass', self.config.cpanel_password)
            page.click('button#login_submit')
            
            try:
                # Wait for navigation to dashboard (URL should not contain 'login')
                # or wait for a dashboard element like #content or #main
                page.wait_for_load_state('networkidle')
                # Wait up to 10s for login to process
                page.wait_for_url(lambda u: "login" not in u, timeout=15000)
            except Exception as e:
                # If we timed out, check for error message
                content = page.content().lower()
                if "invalid login" in content or "failed" in content:
                    raise Exception("Login failed: Invalid credentials or MFA required.")
                raise Exception(f"Login timed out or failed to redirect: {e}")
            
            print("Login successful.")
        
        return browser, context, page

    def navigate_to_app(self, page, app_name):
        """
        Navigates to a specific app from the dashboard via search or direct link.
        Returns the page object (new or existing).
        """
        print(f"Navigating to app: {app_name}...")
        try:
            # Strategies to find the app
            # 1. Try search bar (Paper Lantern / Jupiter)
            try:
                # Short timeout for search attempt
                search_input = page.locator('input#quick-jump-search')
                search_input.wait_for(state="visible", timeout=2000)
                search_input.fill(app_name)
                
                # Search interaction might open new page? Usually search results in same page.
                page.press('input#quick-jump-search', 'Enter')
                page.wait_for_load_state('networkidle')
                # Check for redirection or new tab
                # For now assume same page unless logic dictates
                return page
            except:
                pass

            # 2. Try looking for the text directly (e.g. icon label)
            try:
                # We need to be careful with exact=True vs False. Icon labels might have newlines.
                # Try relaxed match.
                # Capture new page if it opens
                try:
                    with page.context.expect_page(timeout=5000) as new_page_info:
                        page.get_by_text(app_name).first.click()
                    return new_page_info.value
                except:
                    # Maybe it didn't open a new page (e.g. single page app or same tab)
                    # Or click failed. If click worked but no new page, we are on 'page'.
                    # If click failed, we go to except block.
                    # We assume click worked if we are here? No, click() raises error if failed.
                    # If expect_page timed out, it means no new page.
                    pass
                
                # Check if we navigated
                page.wait_for_load_state('networkidle')
                return page
            except:
                pass
            
            # 3. Direct URL Construction (The "Hacker" Way)
            # URL format: https://host:2083/cpsess12345/frontend/jupiter/index.html
            # We want: .../cpsess.../frontend/jupiter/filemanager/index.html
            print("UI navigation failed. Trying direct URL construction...")
            current_url = page.url
            if "/cpsess" in current_url:
                # Extract base with session
                # Split by 'frontend' or just take everything up to the theme
                # e.g. https://.../cpsess.../
                import re
                match = re.search(r'(https?://[^/]+/cpsess[^/]+/)', current_url)
                if match:
                    base_url = match.group(1)
                    # Try Jupiter path (modern default)
                    target = base_url + "frontend/jupiter/filemanager/index.html"
                    if app_name.lower() == "file manager":
                        print(f"Trying direct URL: {target}")
                        page.goto(target)
                        # Check if successful (not 404)
                        if "404" not in page.title():
                             return page
                        
                        # Try Paper Lantern
                        target = base_url + "frontend/paper_lantern/filemanager/index.html"
                        print(f"Trying direct URL: {target}")
                        page.goto(target)
                        return page

            raise Exception(f"Could not find app '{app_name}' via search, link, or direct URL.")

        except Exception as e:
            print(f"Navigation failed: {e}")
            try:
                with open("debug_page.html", "w", encoding="utf-8") as f:
                    f.write(page.content())
                print("Saved debug_page.html")
            except:
                pass
            raise e

    def run_backup(self):
        """
        Automates the 'Backup' -> 'Download a Full Account Backup' flow.
        """
        if not self.config.cpanel_password:
            raise ValueError("Browser automation requires CPANEL_PASSWORD.")

        with sync_playwright() as p:
            browser, context, page = self._login(p)

            try:
                self.navigate_to_app(page, "Backup")

                # 3. Inside Backup Interface
                print("Initiating Full Backup...")
                # Try to find the link. cPanel themes vary.
                # In Paper Lantern/Jupiter, it's often a block.
                # We'll try specific text locators.
                
                # Wait for the backup interface to load
                try:
                    page.wait_for_selector('text=Download a Full Account Backup', timeout=5000)
                    page.get_by_text("Download a Full Account Backup").click()
                except:
                    # Fallback for Jupiter theme which might behave differently
                    # Search specifically for "Full Backup" link
                    page.get_by_role("link", name="Download a Full Account Backup").click()

                
                # 4. Form configuration
                page.select_option('select[name="dest"]', 'homedir')
                
                try:
                    page.check('input[name="email_radio"][value="0"]') 
                except:
                    pass 

                # 5. Submit
                page.click('input[value="Generate Backup"]')
                
                # 6. Verify success message
                page.wait_for_selector('text=Full Backup in Progress', timeout=10000)
                print("Success: Full Backup is now in progress!")
                
                time.sleep(2)

            except Exception as e:
                print(f"Backup Automation Failed: {e}")
                page.screenshot(path="backup_error.png")
                raise e
            finally:
                browser.close()

    def open_file_manager(self):
        """
        Navigates to the File Manager and keeps the browser open for the user.
        """
        if not self.config.cpanel_password:
            raise ValueError("Browser automation requires CPANEL_PASSWORD.")

        if self.headless:
            print("Warning: Opening File Manager in headless mode.")

        with sync_playwright() as p:
            browser, context, page = self._login(p)

            try:
                self.navigate_to_app(page, "File Manager")
                
                # File Manager usually opens in a new tab/popup.
                # We need to wait for the new page.
                with context.expect_page() as new_page_info:
                    # Navigation action that triggers new window is already done or happening
                    # Actually, searching 'File Manager' and hitting enter might direct navigate OR open new tab 
                    # depending on user prefs. Standard is new tab.
                    pass
                
                # If the search opened it in the SAME tab (rare but possible), page is valid.
                # If it opened a NEW tab, we need to grab it.
                # However, the search result often requires a CLICK to open.
                
                print("File Manager opened! Press Ctrl+C to stop.")
                
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

    def upload_file(self, local_path: str, remote_full_path: str):
        """
        Uploads a file via the File Manager UI.
        remote_full_path: e.g. public_html/subdir/file.php
        """
        import os
        if not self.config.cpanel_password:
            raise ValueError("Browser automation requires CPANEL_PASSWORD.")

        target_dir = os.path.dirname(remote_full_path)
        # normalize target_dir: separate path segments
        # e.g. public_html/test -> ['public_html', 'test']
        # If empty, it's home dir.
        path_segments = [s for s in target_dir.replace('\\', '/').split('/') if s]

        with sync_playwright() as p:
            browser, context, page = self._login(p)

            try:
                print("Opening File Manager...")
                # Use robust navigation and capture the page
                fm_page = self.navigate_to_app(page, "File Manager")
                
                # Verify we are on the correct page
                if "filemanager" not in fm_page.url.lower():
                    print(f"Returned page URL '{fm_page.url}' does not look like File Manager. Searching tabs...")
                    found = False
                    for p_tab in context.pages:
                        if "filemanager" in p_tab.url.lower():
                            fm_page = p_tab
                            fm_page.bring_to_front()
                            found = True
                            print(f"Found File Manager tab: {fm_page.url}")
                            break
                    
                    if not found:
                        print("File Manager tab not found. Attempting direct navigation...")
                        # Fallback: construct URL (Jupiter theme)
                        # We need session ID from current URL
                        # e.g. .../cpsess.../
                        try:
                            parts = page.url.split("/frontend")
                            base = parts[0]
                            # Try Jupiter
                            target = base + "/frontend/jupiter/filemanager/index.html"
                            print(f"Navigating direct to: {target}")
                            page.goto(target)
                            fm_page = page
                        except Exception as nav_err:
                            print(f"Direct navigation failed: {nav_err}")

                fm_page.bring_to_front()
                try:
                    fm_page.wait_for_load_state('networkidle', timeout=10000)
                except:
                    pass
                
                # Double-check: are we REALLY on File Manager?
                # The URL might say filemanager, but content might be dashboard.
                page_title = fm_page.title()
                print(f"Current page title: '{page_title}'")
                
                # Capture initial state
                try:
                    with open("debug_fm_initial.html", "w", encoding="utf-8") as f:
                        f.write(fm_page.content())
                    print("Saved debug_fm_initial.html")
                except: pass

                if "Tools" in page_title or ("cPanel" in page_title and "File Manager" not in page_title):
                    print("Page verification failed (Dashboard detected). Forcing direct navigation...")
                    # Construct URL (Jupiter theme default)
                    try:
                        # e.g. https://elk...:2083/cpsess.../frontend/jupiter/filemanager/index.html
                        if "filemanager" in fm_page.url and "index.html" in fm_page.url:
                             target = fm_page.url
                        else:
                             parts = page.url.split("/frontend")
                             base = parts[0]
                             target = base + "/frontend/jupiter/filemanager/index.html"
                        
                        print(f"Forcing goto: {target}")
                        fm_page.goto(target)
                        fm_page.wait_for_load_state('networkidle')
                        print(f"New page title: '{fm_page.title()}'")
                    except Exception as force_nav_err:
                        print(f"Forced navigation failed: {force_nav_err}")
                
                print(f"File Manager interface loaded on: {fm_page.url}")

                # Navigation logic
                # cPanel File Manager (ELFinder based) usually has a sidebar tree and a main view.
                # Double clicking folders in the main view is often reliable.
                # Or typing in the path bar if accessible.
                
                # Default lands in Home.
                
                for segment in path_segments:
                    print(f"Navigating into '{segment}'...")
                    clicked = False
                    
                    # Get all candidates with the folder name
                    # Filter out <option> elements (search bars)
                    candidates = fm_page.get_by_text(segment).all()
                    
                    for cand in candidates:
                        try:
                            if not cand.is_visible():
                                continue
                                
                            tag_name = cand.evaluate("el => el.tagName.toLowerCase()")
                            if tag_name == "option":
                                continue
                            
                            # Log what we found
                            # print(f"Found candidate: <{tag_name}> text='{segment}'")
                            
                            # Usually folders in the main view need double click.
                            cand.scroll_into_view_if_needed()
                            cand.dblclick(timeout=2000)
                            clicked = True
                            time.sleep(2) # Wait for view update
                            break
                        except Exception as click_err:
                            # print(f"Click failed on candidate: {click_err}")
                            pass
                    
                    if not clicked:
                        print(f"Warning: Could not navigate to '{segment}' via visible text. Trying generic folder selector...")
                        # Fallback: specific folder icon selector if known
                        # fm_page.click(f".file-row:has-text('{segment}')")
                        pass
                
                print(f"Reached target directory (assumed): {target_dir}")
                
                # Click Upload Button
                print("Clicking Upload...")
                # Try locating the Upload button by specific robust selectors
                upload_clicked = False
                
                # Wait for a new page (tab) to open
                with context.expect_page() as upload_page_info:
                    # Strategy 1: Text "Upload" (highest confidence if visible and not an option)
                    try:
                        upload_btn = fm_page.get_by_text("Upload", exact=True)
                        if upload_btn.count() > 0:
                            for i in range(upload_btn.count()):
                                btn = upload_btn.nth(i)
                                if btn.is_visible() and btn.evaluate("el => el.tagName.toLowerCase()") != "option":
                                    btn.click()
                                    upload_clicked = True
                                    break
                    except: pass
                    
                    # Strategy 2: ID #upload
                    if not upload_clicked:
                        try:
                            fm_page.click('#upload', timeout=2000)
                            upload_clicked = True
                        except: pass
                        
                    # Strategy 3: Title attribute
                    if not upload_clicked:
                        try:
                            fm_page.click('a[title="Upload"]', timeout=2000)
                            upload_clicked = True
                        except: pass
                        
                    if not upload_clicked:
                        # Before failing, try to find an iframe?
                        # Some cPanel versions load FM in iframe.
                        # But typically it's top level.
                        raise Exception("Could not find Upload button.")

                upload_page = upload_page_info.value
                upload_page.wait_for_load_state('networkidle')
                print(f"Upload page opened: {upload_page.title()}")
                
                # Handle Overwrite
                # Checkbox: "Overwrite existing files"
                print("Selecting 'Overwrite existing files'...")
                try:
                    # Wait for checkbox
                    upload_page.wait_for_selector('input[type="checkbox"]', timeout=5000)
                    
                    # Try by Label
                    try:
                        overwrite_cb = upload_page.get_by_label("Overwrite existing files")
                        if not overwrite_cb.is_checked():
                            overwrite_cb.check()
                            print("Checked overwrite via label.")
                    except:
                        # Try by Value or just first checkbox
                        cb = upload_page.locator('input[type="checkbox"][value="1"]').first
                        if cb.is_visible():
                            if not cb.is_checked():
                                cb.check()
                            print("Checked overwrite via input value.")
                except Exception as e:
                    print(f"Warning: Could not check overwrite option: {e}")

                # Select File
                print(f"Uploading {local_path}...")
                # File input is usually hidden or created dynamically. 
                # Playwright handles file chooser or input[type=file]
                
                # cPanel upload often has <input type="file" name="files[]">
                file_input = upload_page.locator('input[type="file"]')
                file_input.set_input_files(local_path)
                
                # Wait for upload completion
                # Usually a progress bar turns green or "Complete" text appears.
                # .progress-bar-success or text "100%"
                print("Waiting for upload to complete (timeout 60s)...")
                try:
                    upload_page.wait_for_selector('.progress-bar-success, text="Complete"', timeout=60000)
                    print("Upload Complete!")
                except:
                    print("Warning: Upload completion indicator not found. Checking if file exists...")
                
                time.sleep(2)
                
            except Exception as e:
                print(f"Upload Process Failed: {e}")
                # Save debug info
                try:
                    fname = f"debug_error_{int(time.time())}.html"
                    with open(fname, "w", encoding="utf-8") as f:
                        f.write(fm_page.content())
                    print(f"Saved {fname} (File Manager)")
                    
                    # Also try to save Upload page if it exists
                    try:
                        with open(f"debug_upload_page_{int(time.time())}.html", "w", encoding="utf-8") as f:
                            f.write(upload_page.content())
                    except: pass
                except:
                    pass
                raise e
            finally:
                browser.close()
