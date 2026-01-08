
import asyncio
import os
import json
import re
from agents.base import BaseAgent
from utils.cpanel_manager import CPanelManager
from utils.browser_manager import BrowserManager
from database import save_managed_account, get_registration_macro, add_registration_task

class AccountCreatorAgent(BaseAgent):
    def __init__(self, cpanel_config):
        super().__init__(
            role="Account Creator", 
            goal="Automate the creation and verification of user accounts."
        )
        self.cpanel = CPanelManager(
            cpanel_config['url'],
            cpanel_config['user'],
            cpanel_config['token']
        )
        self.default_domain = cpanel_config.get('domain')
        # Unique session for isolation
        self.browser_manager = BrowserManager(session_id=f"creator_{os.urandom(4).hex()}")

    async def create_account(self, platform_name, registration_url, account_details=None, proxy=None):
        """
        Main flow to create an account.
        1. Generate Email
        2. Fill Registration Form
        3. Verify Email
        """
        # 1. Generate Email
        email_user = f"{platform_name.lower().replace(' ', '')}.{os.urandom(2).hex()}"
        
        # Domain logic: Config > Inference
        if self.default_domain:
            domain = self.default_domain
        else:
            # Fallback to cPanel host (risky but better than nothing)
            domain = self.cpanel.cpanel_url.replace("https://", "").replace("http://", "").split(":")[0]
            
        email_addr = f"{email_user}@{domain}"
        email_pass = os.urandom(8).hex() + "A1!"
        
        print(f"Creating email: {email_addr}")
        res = self.cpanel.create_email_account(email_addr, email_pass)
        if res['status'] != 'success':
            print(f"Email creation failed: {res['message']}. Logging manual task.")
            # Store error in details for UI visibility
            if account_details is None: account_details = {}
            account_details['error'] = f"Email creation failed: {res['message']}"
            add_registration_task(platform_name, registration_url, account_details)
            return f"Email creation failed: {res['message']} (Task created)"

        # 2. Registration
        page = await self.browser_manager.launch(headless=False, proxy=proxy)
        try:
            # Check for existing macro
            macro = get_registration_macro(platform_name)
            if macro:
                print(f"Macro found for {platform_name}. Replaying...")
                res = await self._replay_macro(page, registration_url, json.loads(macro['steps']), email_addr, email_pass, account_details)
                if res == "success":
                    status = "verified_via_macro"
                    # Proceed to verification/saving
                else:
                    print(f"Macro replay failed: {res}. Falling back to AI...")
                    # Continue to AI flow if macro fails? Or just fail?
                    # Let's try AI flow as fallback.
            
            if not macro or (macro and res != "success"):
                print(f"Navigating to {registration_url}")
                await page.goto(registration_url, timeout=120000, wait_until="domcontentloaded")
                try:
                    await page.wait_for_load_state("networkidle", timeout=15000)
                except:
                    print("Networkidle timeout, proceeding...")

            selectors = {}
            # Max 2 attempts (Initial -> Click Signup -> Analyzing)
            for attempt in range(2):
                content = await page.content()
                cleaned_content = self._clean_html(content)
                
                prompt = f"""
                Analyze this HTML and return a JSON object with CSS selectors for the *Registration/Sign Up* form fields.
                
                CRITICAL NAVIGATION INFO:
                - If we are on a Login page, I need the selector to switch to 'Sign Up' or 'Register'.
                - The link might be in the bottom corners or obscured by JS (no href). 
                - Look for 'div', 'span', or 'a' tags containing text "Sign Up", "Register", or "Create Account".
                
                Return JSON:
                {{
                    "email_input": "css_selector", 
                    "username_input": "css_selector (or null)", 
                    "password_input": "css_selector", 
                    "submit_button": "css_selector",
                    "signup_link": "css_selector (for the Sign Up/Register text element)"
                }}
                
                HTML: {cleaned_content[:4000]}
                """
                response = self.prompt(prompt, "Return ONLY JSON.")
                selectors = self._parse_json(response)
                print(f"Analysis Attempt {attempt+1}: {selectors}")
                
                if selectors.get("signup_link") and not selectors.get("email_input"):
                    print("Clicking Sign Up link...")
                    try:
                        # Robust Click Strategy
                        link_sel = selectors["signup_link"]
                        # 1. Try Selector
                        try:
                            await page.click(link_sel, timeout=3000)
                        except:
                            # 2. Try Text Match Logic (Fallback)
                            print("Selector click failed, trying text match...")
                            found = False
                            for txt in ["Sign up", "Sign Up", "Register", "Create account", "Get started"]:
                                try:
                                    await page.get_by_text(txt, exact=False).first.click(timeout=2000)
                                    found = True
                                    break
                                except:
                                    continue
                            if not found:
                                # Try JS click on selector
                                await page.eval_on_selector(link_sel, "e => e.click()")

                        await page.wait_for_load_state("networkidle", timeout=10000)
                        continue # Re-analyze
                    except Exception as e:
                        print(f"Failed to click signup link: {e}")
                        break
                
                if selectors.get("email_input"):
                    break # Found form!
            
            # Fill Form
            if selectors.get("email_input"):
                # Check for captcha before/during fill
                await self.browser_manager.solve_captcha_if_present()
                await page.fill(selectors["email_input"], email_addr)
            else:
                print("FAIL: Failed to find registration form.")
                add_registration_task(platform_name, registration_url, account_details)
                return "failed_no_form_task_created"

            if selectors.get("username_input") and account_details.get("username"):
                await page.fill(selectors["username_input"], account_details["username"])
            if selectors.get("password_input"):
                await page.fill(selectors["password_input"], email_pass)
                
            # Submit
            if selectors.get("submit_button"):
                await page.click(selectors["submit_button"])
                await page.wait_for_load_state("networkidle")
            
            # 3. Verification Loop
            print("Checking for verification email...")
            email_content = self.cpanel.check_imap_for_verification(email_addr, email_pass)
            
            if email_content:
                print("Verification email received.")
                # AI to extract link or code
                verify_prompt = f"""
                Extract the verification link or code from this email body.
                Return JSON: {{"link": "http...", "code": "12345"}}
                Body: {email_content['body']}
                """
                v_res = self.prompt(verify_prompt, "Return ONLY JSON.")
                v_data = self._parse_json(v_res)
                
                if v_data.get("link"):
                    await page.goto(v_data["link"])
                    await page.wait_for_load_state("networkidle")
                    status = "verified"
                elif v_data.get("code"):
                    # We would need to find where to input the code. 
                    # For now just save it.
                    status = "verified_code_received"
                else:
                    status = "verification_failed"
            else:
                status = "verification_timeout"
 
            # Save to DB
            save_managed_account(
                platform_name,
                email_addr,
                account_details.get("username", email_user),
                email_pass,
                metadata={"verification_data": email_content}
            )
            
            return f"Account process finished with status: {status}"
 
        except Exception as e:
            print(f"Error during registration: {e}")
            add_registration_task(platform_name, registration_url, account_details)
            return f"Error during registration: {e} (Task created)"
        finally:
            await self.browser_manager.close()

    async def _replay_macro(self, page, url, steps, email, password, details):
        """Replays a recorded macro."""
        try:
            print(f"Navigating to {url} for macro replay...")
            await page.goto(url, wait_until="networkidle")
            
            for step in steps:
                stype = step.get('type')
                selector = step.get('selector')
                value = step.get('value')
                
                print(f"Replaying step: {stype} on {selector} (Text: {step.get('innerText')})")
                
                # Handle placeholders in value
                if value:
                    if "{email}" in value:
                        value = value.replace("{email}", email)
                    if "{password}" in value:
                        value = value.replace("{password}", password)
                    if "{username}" in value:
                        value = value.replace("{username}", details.get('username', 'user'))

                # Selector fallback strategy
                selectors_to_try = [selector]
                if step.get('innerText'):
                    selectors_to_try.append(f"text='{step['innerText']}'")
                if step.get('placeholder'):
                    selectors_to_try.append(f"[placeholder='{step['placeholder']}']")
                if step.get('ariaLabel'):
                    selectors_to_try.append(f"[aria-label='{step['ariaLabel']}']")

                success = False
                for sel in selectors_to_try:
                    try:
                        if stype == 'click':
                            await page.click(sel, timeout=3000)
                        elif stype == 'change':
                            await page.fill(sel, value, timeout=3000)
                        success = True
                        break
                    except:
                        # Before giving up on this step, try dismissing popups
                        if await self._dismiss_popups(page):
                            # Try the same selector again after dismissal
                            try:
                                if stype == 'click':
                                    await page.click(sel, timeout=2000)
                                elif stype == 'change':
                                    await page.fill(sel, value, timeout=2000)
                                success = True
                                break
                            except:
                                continue
                        continue
                
                if not success:
                    print(f"Warning: Failed to replay step on all selectors: {selectors_to_try}")
                    # Final attempt: Coordinates (if available) - risky but may work on fixed layouts
                    if step.get('x') and step.get('y'):
                        print(f"Attempting click via coordinates: {step['x']}, {step['y']}")
                        try:
                            await page.mouse.click(step['x'], step['y'])
                            success = True
                        except:
                            pass
                
                await page.wait_for_timeout(500)
            
            return "success"
        except Exception as e:
            print(f"Macro replay error: {e}")
            return str(e)

    async def _dismiss_popups(self, page):
        """Heuristic to dismiss common modas/popups."""
        close_selectors = [
            "[aria-label='Close']",
            "button:has-text('Close')",
            "text='✕'",
            "text='Maybe later'",
            "button:has-text('Dismiss')",
            ".modal-close",
            ".close-button"
        ]
        dismissed = False
        for sel in close_selectors:
            try:
                btn = page.locator(sel).first
                if await btn.is_visible(timeout=1000):
                    print(f"Dismissing pop-up via: {sel}")
                    await btn.click()
                    dismissed = True
                    await page.wait_for_timeout(500)
            except:
                continue
        return dismissed
 
    def _clean_html(self, html):
        """Simple cleaner to reduce token usage."""
        # Remove head, scripts, styles, svgs, comments, meta, link
        html = re.sub(r'<head.*?</head>', '', html, flags=re.DOTALL)
        html = re.sub(r'<(script|style|svg|noscript|meta|link).*?>.*?</\1>', '', html, flags=re.DOTALL) # for tags with closing
        html = re.sub(r'<(script|style|svg|noscript|meta|link).*?>', '', html, flags=re.DOTALL) # for self-closing or malformed
        html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
        # Collapse whitespace
        html = re.sub(r'\s+', ' ', html)
        return html

    def _parse_json(self, text):
        try:
            # Try to find JSON block
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group(0))
            return json.loads(text)
        except:
            return {}

    async def think_async(self, message):
        """ Entry point for the agent. """
        # Expecting message JSON like: {"action": "create", "platform": "...", "url": "..."}
        try:
            data = json.loads(message)
            if data.get("action") == "create":
                return await self.create_account(
                    data.get("platform"),
                    data.get("url"),
                    data.get("details", {})
                )
        except:
            return "Invalid input format."
    
    def think(self, message):
        # Wrapper for async
        pass
