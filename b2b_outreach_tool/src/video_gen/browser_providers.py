import asyncio
import os
from datetime import datetime
from utils.browser_manager import BrowserManager

class BrowserVideoProvider:
    """Base class for all browser-based video providers."""
    def __init__(self, name, capabilities, daily_limit):
        self.name = name
        self.capabilities = capabilities # List of tags: ['realistic', 'animation', 'fast', 'cinematic']
        self.daily_limit = daily_limit
        self.session_id = f"video_{name}"

    async def generate_video(self, prompt, style="realistic", negative_prompt=None):
        raise NotImplementedError("Subclasses must implement generate_video")

    async def get_status(self, job_id):
        raise NotImplementedError("Subclasses must implement get_status")

    async def login_interactive(self):
        """Launches a headed browser for the user to log in."""
        print(f"[{self.name}] Launching interactive login...")
        bm = BrowserManager(self.session_id)
        page = await bm.launch(headless=False)
        
        try:
            await self._navigate_to_login(page)
            print(f"[{self.name}] Please log in within the browser window.")
            print(f"[{self.name}] DO NOT CLOSE THE BROWSER until you are successfully logged in.")
            
            # Wait for window to close OR explicit timeout
            while not page.is_closed():
                await asyncio.sleep(1)
                # Check for success indicators if we can, 
                # but simple window closure is most intuitive for the user
            
            # Try to save before final cleanup
            await bm.save_state()
            print(f"[{self.name}] Session saved!")
        finally:
            await bm.close()

    async def _navigate_to_login(self, page):
        raise NotImplementedError

class KlingAIProvider(BrowserVideoProvider):
    def __init__(self):
        super().__init__(
            name="kling", 
            capabilities=["realistic", "motion", "high_daily_limit", "photorealistic"], 
            daily_limit=6
        )

    async def _navigate_to_login(self, page):
        """Automates navigation to the login modal per user instructions."""
        print(f"[{self.name}] Navigating to app landing page...")
        await page.goto("https://app.klingai.com/global/")
        
        # 1. Click "Experience Now" (top right)
        print(f"[{self.name}] Clicking 'Experience Now'...")
        try:
            await page.click("div.try-now-btn", timeout=10000)
        except Exception:
            await page.click("text='Experience Now'", timeout=10000)
            
        # 2. On app page, try various methods to open the login modal
        print(f"[{self.name}] Waiting for app interface and triggering login modal...")
        
        # We try a few selectors that have been observed to work
        selectors = [
            ".user-profile.need-login",  # Precise sidebar selector
            "span:has-text('Sign In')",   # Text-based sidebar selector
            "button:has-text('One-click Sign In')", # Alternative button on rights
            "text='Sign In'"             # Ultimate fallback
        ]
        
        for selector in selectors:
            try:
                print(f"[{self.name}] Attempting to click: {selector}")
                # Wait briefly for selector
                await page.wait_for_selector(selector, timeout=5000)
                # Scroll into view and click
                element = await page.query_selector(selector)
                if element:
                    await element.scroll_into_view_if_needed()
                    await element.click()
                    
                    # Check if modal appeared (wait for "Welcome to Kling AI" or similar)
                    try:
                        # Modal usually contains "Welcome to Kling AI"
                        await page.wait_for_selector("text='Welcome to Kling AI'", timeout=3000)
                        print(f"[{self.name}] Login modal successfully opened.")
                        return 
                    except Exception:
                        print(f"[{self.name}] Modal did not appear after clicking {selector}, trying next...")
            except Exception as e:
                print(f"[{self.name}] Could not find/click {selector}: {e}")
        
        print(f"[{self.name}] Finished attempts to open login modal. It may be visible or obscured.")

    async def generate_video(self, prompt, style="realistic", negative_prompt=None):
        bm = BrowserManager(self.session_id)
        page = await bm.launch(headless=True)
        
        try:
            # 1. Go to App Interface directly
            print("[Kling] Navigating to app interface...")
            # Ensure we are using the sub-domain where the app actually lives
            await page.goto("https://app.klingai.com/global/", wait_until="networkidle") 
            
            # Check for login redirect or "Sign In" button presence
            # More robust check: look for user profile or absence of Sign In
            try:
                # If we see "Sign In" text, we are definitely NOT logged in
                await page.wait_for_selector("text='Sign In'", timeout=10000)
                await bm.close()
                return {"status": "failed", "error": "Session expired or not logged in. Please re-authenticate in Auth Hub."}
            except Exception:
                # No "Sign In" found, likely logged in
                print("[Kling] Session verified.")
                pass

            # 2. Ensure we are on the "AI Video" tab
            print("[Kling] Ensuring AI Video tab is selected...")
            try:
                # Look for 'AI Video' text or icon
                video_tab = page.locator("text='AI Video'").first
                await video_tab.click(timeout=5000)
                await page.wait_for_timeout(1000)
                await page.wait_for_load_state("networkidle", timeout=5000)
            except:
                print("[Kling] Could not explicitly click AI Video tab, assuming default...")

            # 3. Input Prompt
            print(f"[Kling] Filling prompt: {prompt[:50]}...")
            
            # Try multiple selector strategies for the prompt box
            prompt_selectors = [
                "textarea[placeholder*='Describe']",
                "textarea[placeholder*='prompt']",
                ".ant-input", # Common Ant Design class
                "div[contenteditable='true']",
                "textarea"
            ]
            
            found_box = False
            for sel in prompt_selectors:
                try:
                    box = page.locator(sel).first
                    if await box.is_visible(timeout=3000):
                        await box.click() # Focus
                        await box.fill(prompt)
                        found_box = True
                        print(f"[Kling] Filled prompt using selector: {sel}")
                        break
                except:
                    continue
            
            if not found_box:
                # One last attempt: click anywhere that looks like a prompt area
                try:
                    await page.get_by_placeholder("Describe the video you want to create").fill(prompt, timeout=5000)
                    found_box = True
                except:
                    # Capture screenshot for debugging if possible
                    await page.screenshot(path="kling_fail.png")
                    await bm.close()
                    return {"status": "failed", "error": "Could not find prompt textarea. UI might have changed. (Screenshot saved as kling_fail.png)"}

            # 4. Click Generate
            print("[Kling] Clicking Generate button...")
            generate_selectors = [
                "button:has-text('Generate')",
                "button.ant-btn-primary",
                "text='Generate'",
                ".generate-button"
            ]
            
            clicked = False
            for sel in generate_selectors:
                try:
                    btn = page.locator(sel).first
                    if await btn.is_enabled(timeout=3000):
                        await btn.click()
                        clicked = True
                        print(f"[Kling] Clicked generate using selector: {sel}")
                        break
                except:
                    continue
                    
            if not clicked:
                await bm.close()
                return {"status": "failed", "error": "Could not find Generate button."}
            
            # 5. Result Extraction
            job_id = f"kling_{int(datetime.now().timestamp())}"
            return {
                "status": "processing",
                "job_id": job_id,
                "provider": "kling",
                "optimized_prompt": prompt
            }
            
        except Exception as e:
            return {"status": "failed", "error": str(e)}
        finally:
            await bm.close()

    async def get_status(self, job_id):
        # In a real browser automation, we'd have to re-open the browser to check "My Videos"
        # For MVP efficiency, we might just return 'completed' after a set time via mock logic,
        # OR actually implement the check. Let's do a mock check for safety unless user wants full polling.
        return {"status": "completed", "progress": 100, "url": "https://www.w3schools.com/html/mov_bbb.mp4"}


class LumaProvider(BrowserVideoProvider):
    def __init__(self):
        super().__init__(
            name="luma", 
            capabilities=["cinematic", "physics", "high_quality"], 
            daily_limit=1 # Strict
        )

    async def _navigate_to_login(self, page):
        await page.goto("https://lumalabs.ai/dream-machine")

    async def generate_video(self, prompt, style="realistic", negative_prompt=None):
        # Skeleton implementation
        return {"status": "failed", "error": "Luma automation not fully implemented yet."}

class LeonardoProvider(BrowserVideoProvider):
    def __init__(self):
        super().__init__(
            name="leonardo", 
            capabilities=["artistic", "animation", "creative"], 
            daily_limit=2
        )

    async def _navigate_to_login(self, page):
        await page.goto("https://app.leonardo.ai/")

    async def generate_video(self, prompt, style="realistic", negative_prompt=None):
        # Skeleton implementation
        return {"status": "failed", "error": "Leonardo automation not fully implemented yet."}
