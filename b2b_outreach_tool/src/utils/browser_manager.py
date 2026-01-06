import os
import json
import asyncio
from playwright.async_api import async_playwright
from database import get_captcha_settings
from utils.captcha_solver import CaptchaSolver

class BrowserManager:
    """
    Manages Playwright browser sessions with persistence.
    Allows re-using login states (cookies/storage) across runs.
    """
    def __init__(self, session_id="default"):
        self.session_id = session_id
        self.storage_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "sessions", f"{session_id}.json")
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
        
        # Ensure sessions dir exists
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)

    async def launch(self, headless=True):
        """
        Launches the browser and context.
        Loads existing storage state if available.
        """
        self.playwright = await async_playwright().start()
        
        # Launch options
        self.browser = await self.playwright.chromium.launch(
            headless=headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-infobars'
            ]
        )
        
        # Load state if exists
        state_file = self.storage_path if os.path.exists(self.storage_path) else None
        
        # Create Context
        self.context = await self.browser.new_context(
            storage_state=state_file,
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        
        self.page = await self.context.new_page()
        
        # Attach captcha solver if configured
        self._attach_solver()
        
        return self.page

    def _attach_solver(self):
        """Attaches captcha solver configuration to the page object."""
        captcha_settings = get_captcha_settings()
        if captcha_settings and captcha_settings.get('enabled'):
            self.page.captcha_solver = CaptchaSolver(
                captcha_settings['provider'], 
                captcha_settings['api_key']
            )
        else:
            self.page.captcha_solver = None

    async def save_state(self):
        """Persists the current browser context (cookies, storage) to disk."""
        if self.context:
            await self.context.storage_state(path=self.storage_path)
            print(f"✅ Session saved to {self.storage_path}")

    async def close(self):
        """Closes the browser and playwright."""
        if self.context:
            await self.save_state()
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def solve_captcha_if_present(self):
        """Re-uses the captcha solving logic from previous implementations."""
        # This logic is adapted from seo_bridge to be reusable
        if not hasattr(self.page, 'captcha_solver') or not self.page.captcha_solver:
            return False

        # 1. Detection
        recaptcha_iframe = await self.page.query_selector("iframe[src*='recaptcha/api2/anchor']")
        if recaptcha_iframe:
            print(f"[{self.session_id}] reCAPTCHA detected. Attempting to solve...")
            
             # --- Handle Local Whisper (Audio-based) ---
            if self.page.captcha_solver.provider == "local-whisper":
                return await self._solve_via_local_audio(recaptcha_iframe)

            # --- Handle External APIs (Token-based) ---
            site_key_match = await self.page.evaluate('''() => {
                const el = document.querySelector(".g-recaptcha");
                return el ? el.getAttribute("data-sitekey") : null;
            }''')
            
            if site_key_match:
                solution = await self.page.captcha_solver.solve_recaptcha_v2(site_key_match, self.page.url)
                if solution.get("status") == "success":
                    token = solution["token"]
                    await self.page.evaluate(f'document.getElementById("g-recaptcha-response").innerHTML="{token}";')
                    return True
        return False

    async def _solve_via_local_audio(self, anchor_iframe):
        """Specific flow for Local Whisper using audio challenges."""
        try:
            # 1. Click the checkbox
            frame = await anchor_iframe.content_frame()
            if frame:
                await frame.click("#recaptcha-anchor")
                await self.page.wait_for_timeout(2000)

                # 2. Find the challenge iframe
                challenge_iframe = await self.page.query_selector("iframe[src*='recaptcha/api2/bframe']")
                if not challenge_iframe:
                    return False
                
                inner_frame = await challenge_iframe.content_frame()
                if inner_frame:
                    # 3. Click Audio Button
                    await inner_frame.click("#recaptcha-audio-button")
                    await self.page.wait_for_timeout(2000)

                    # 4. Get Download Link
                    audio_url = await inner_frame.get_attribute(".rc-audiochallenge-tdownload-link", "href")
                    if not audio_url:
                        return False

                    # 5. Solve via local AI
                    solution = await self.page.captcha_solver.solve_recaptcha_v2(None, self.page.url, audio_url=audio_url)
                    
                    if solution.get("status") == "success":
                        token = solution["token"]
                        await inner_frame.fill("#audio-response", token)
                        await inner_frame.press("#audio-response", "Enter")
                        await self.page.wait_for_timeout(2000)
                        return True
        except Exception as e:
            print(f"Error solving captcha: {e}")
            
        return False
