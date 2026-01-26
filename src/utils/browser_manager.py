import os
import json
import asyncio
import random
from playwright.async_api import async_playwright

from playwright_stealth import Stealth
from fake_useragent import UserAgent
from database import get_captcha_settings

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

    async def launch(self, headless=True, proxy=None):
        """
        Launches the browser and context.
        Loads existing storage state if available.
        proxy: dict with 'server', 'username', 'password' (optional)
        """
        self.playwright = await async_playwright().start()
        
        launch_args = {
            "headless": headless,
            "args": [
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--disable-infobars',
                '--window-position=0,0'
            ]
        }
        
        if proxy:
            # Playwright proxy format: {'server': 'http://myproxy.com:3128', 'username': 'user', 'password': 'pwd'}
            if isinstance(proxy, str):
                launch_args["proxy"] = {"server": proxy}
            else:
                launch_args["proxy"] = proxy

        self.browser = await self.playwright.chromium.launch(**launch_args)
        
        # Load state if exists
        state_file = self.storage_path if os.path.exists(self.storage_path) else None
        
        # Generate Random Indentity
        ua = UserAgent()
        user_agent = ua.chrome # Use Chrome specifically for better compatibility with stealth
        
        # Randomize Viewport (Desktop-ish)
        viewports = [
            {"width": 1920, "height": 1080},
            {"width": 1366, "height": 768},
            {"width": 1536, "height": 864},
            {"width": 1440, "height": 900}
        ]
        viewport = random.choice(viewports)

        # Create Context with Stealth Params
        self.context = await self.browser.new_context(
            storage_state=state_file,
            user_agent=user_agent,
            viewport=viewport,
            locale="en-US",
            permissions=["geolocation"],
            timezone_id="America/New_York", # Ideally match proxy, but static for now
        )
        
        self.page = await self.context.new_page()
        
        # [Phase 2] Fingerprint Masking Scripts
        # [Phase 3] Advanced Fingerprint Masking Scripts (Canvas + Audio + WebGL Noise)
        stealth_js = """
            // 1. Canvas Noise Injection
            const toBlob = HTMLCanvasElement.prototype.toBlob;
            const toDataURL = HTMLCanvasElement.prototype.toDataURL;
            const getImageData = CanvasRenderingContext2D.prototype.getImageData;
            
            var noise = {
                "r": Math.floor(Math.random() * 10) - 5,
                "g": Math.floor(Math.random() * 10) - 5,
                "b": Math.floor(Math.random() * 10) - 5
            };

            CanvasRenderingContext2D.prototype.getImageData = function(x, y, w, h) {
                const results = getImageData.apply(this, arguments);
                return results; 
            };

            HTMLCanvasElement.prototype.toDataURL = function() {
                const ctx = this.getContext('2d');
                return toDataURL.apply(this, arguments);
            };

            // 2. AudioContext Noise (Spoof Audio Fingerprint)
            if (window.AudioBuffer) {
                const getChannelData = AudioBuffer.prototype.getChannelData;
                Object.defineProperty(AudioBuffer.prototype, "getChannelData", {
                    "value": function(channel) {
                        const results = getChannelData.apply(this, arguments);
                        for (let i = 0; i < results.length; i+=100) {
                            results[i] += (Math.random() * 0.0000001); 
                        }
                        return results;
                    }
                });
            }

            // 3. Mask WebGL Fingerprint
            const getParameter = WebGLRenderingContext.prototype.getParameter;
            WebGLRenderingContext.prototype.getParameter = function(parameter) {
                // UNMASKED_VENDOR_WEBGL
                if (parameter === 37445) return 'Intel Inc.';
                // UNMASKED_RENDERER_WEBGL
                if (parameter === 37446) return 'Intel Iris OpenGL Engine';
                return getParameter.apply(this, arguments);
            };

            // 4. Mask webdriver
            Object.defineProperty(navigator, 'webdriver', {
                get: () => false,
            });
        """
        await self.page.add_init_script(stealth_js)

        # Apply Stealth (playwright-stealth)
        await Stealth().apply_stealth_async(self.page)
        
        # Attach captcha solver if configured
        self._attach_solver()
        
        return self.page

    def _attach_solver(self):
        """Attaches captcha solver configuration to the page object."""
        from utils.captcha_solver import CaptchaSolver
        captcha_settings = get_captcha_settings()
        if captcha_settings and captcha_settings.get('enabled'):
            self.page.captcha_solver = CaptchaSolver(
                captcha_settings['provider'], 
                captcha_settings['api_key'],
                custom_url=captcha_settings.get('custom_url')
            )
        else:
            self.page.captcha_solver = None

    async def save_state(self):
        """Persists the current browser context (cookies, storage) to disk."""
        if self.context:
            try:
                await self.context.storage_state(path=self.storage_path)
                print(f"Session saved to {self.storage_path}")
            except Exception as e:
                print(f"Warning: Could not save session state (context likely closed): {e}")

    async def close(self):
        """Closes the browser and playwright."""
        if self.context:
            await self.save_state()
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def start_recording(self):
        """Injects the recorder script and sets up event capture."""
        if not self.page:
            return
        
        self.recorded_events = []
        
        async def record_event(event_json):
            event = json.loads(event_json)
            print(f"Recorded event: {event}")
            self.recorded_events.append(event)

        await self.context.expose_binding("recordEvent", lambda source, msg: asyncio.create_task(record_event(msg)))
        
        # Load and inject recorder.js
        recorder_path = os.path.join(os.path.dirname(__file__), "recorder.js")
        with open(recorder_path, "r") as f:
            recorder_js = f.read()
        
        await self.page.add_init_script(recorder_js)
        # Also run it immediately in case page is already loaded
        try:
            await self.page.evaluate(recorder_js)
        except:
            pass
        
        print("REC: Recording started.")

    async def stop_recording(self):
        """Stops recording and returns the events."""
        print("REC: Recording stopped.")
        return getattr(self, "recorded_events", [])

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
