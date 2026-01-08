from .base import BaseAgent
from utils.browser_manager import BrowserManager
import asyncio
import re
import random

class ContactFormAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            role="Contact Form Specialist",
            goal="Identify and submit personalized messages through website contact forms.",
            provider=provider
        )

    def parse_spintax(self, text):
        """Standard spintax parser {option1|option2|option3}"""
        pattern = re.compile(r'\{([^{}]*)\}')
        while True:
            match = pattern.search(text)
            if not match:
                break
            choices = match.group(1).split('|')
            text = text.replace(match.group(0), random.choice(choices), 1)
        return text

    async def submit_contact_form(self, url, lead_data, message_template, status_callback=None):
        """
        Attempts to find and submit a contact form on the given URL.
        lead_data: dict with 'name', 'email', 'website', 'company', etc.
        message_template: string with spintax.
        """
        if status_callback: status_callback(f"🌐 Navigating to {url}...")
        
        browser = BrowserManager(session_id=f"contact_{random.randint(1000, 9999)}")
        try:
            page = await browser.launch(headless=True)
            await page.goto(url, wait_until="networkidle")
            
            # 1. Ensure we are on a contact page
            current_url = page.url.lower()
            if "contact" not in current_url:
                if status_callback: status_callback("🔍 Searching for contact link...")
                contact_link = await page.query_selector("a:text-is('Contact'), a:text-is('Contact Us'), a[href*='contact']")
                if contact_link:
                    await contact_link.click()
                    await page.wait_for_load_state("networkidle")
            
            # 2. Identify Form and Fields via LLM
            if status_callback: status_callback("🤖 Analyzing form fields...")
            html_snippet = await page.content()
            # Truncate to save tokens, focus on form elements
            form_html = self._extract_form_html(html_snippet)
            
            mapping_prompt = (
                f"Analyze this form HTML and map the fields to the following lead context:\n"
                f"Context: {lead_data}\n\n"
                f"Form HTML:\n{form_html[:4000]}\n\n"
                "Return a JSON mapping of { 'css_selector': 'value' } where 'value' is either the corresponding field from context "
                "or a hardcoded string. Only include input, textarea, and select fields. Do not include the submit button yet."
            )
            
            field_mapping = self.generate_json(mapping_prompt)
            if not field_mapping:
                return {"status": "failed", "reason": "Could not map form fields"}
            
            # 3. Fill the form
            if status_callback: status_callback("✍️ Filling form...")
            for selector, value in field_mapping.items():
                try:
                    # Process spintax if value is the message
                    if value == message_template:
                        value = self.parse_spintax(value)
                    
                    await page.fill(selector, str(value))
                except Exception as e:
                    if status_callback: status_callback(f"⚠️ Warning filling {selector}: {e}")

            # 4. Handle Captcha
            if status_callback: status_callback("🧩 Checking for captchas...")
            await browser.solve_captcha_if_present()
            
            # 5. Submit
            if status_callback: status_callback("🚀 Submitting...")
            submit_btn = await page.query_selector("input[type='submit'], button[type='submit'], button:text-is('Send'), button:text-is('Submit')")
            if submit_btn:
                await submit_btn.click()
                await page.wait_for_timeout(3000) # Wait for response
                
                # Check for success indicators
                final_html = await page.content()
                success_keywords = ["thank you", "received", "success", "sent", "message has been"]
                if any(kw in final_html.lower() for kw in success_keywords):
                    return {"status": "success", "url": page.url}
                else:
                    return {"status": "partial", "detail": "Submitted but no clear success message found."}
            else:
                return {"status": "failed", "reason": "No submit button found"}

        except Exception as e:
            return {"status": "error", "reason": str(e)}
        finally:
            await browser.close()

    def _extract_form_html(self, html):
        """Simple extraction of form tags to reduce token usage."""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        forms = soup.find_all('form')
        return "\n".join([str(f) for f in forms])
