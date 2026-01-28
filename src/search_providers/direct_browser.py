import asyncio
import random
import os
from utils.browser_manager import BrowserManager

class DirectBrowser:
    """
    Implements a 'Direct Search' strategy using a visible (headed) browser 
    to emulate human behavior and bypass anti-bot protections.
    
    [UPDATED] Uses BrowserManager for advanced stealth (Canvas/Audio masking) and persistence.
    """
    
    def __init__(self, headless=False, session_id="direct_search", proxy=None):
        self.headless = headless
        self.session_id = session_id
        self.proxy = proxy
        # Human-like delays
        self.MIN_TYPING_DELAY = 100
        self.MAX_TYPING_DELAY = 300
        self.MIN_PAGE_DELAY = 2000
        self.MAX_PAGE_DELAY = 5000
        self.browser_manager = None

    async def _human_type(self, page, selector, text):
        """Types text into a selector with random delays between keystrokes."""
        try:
            await page.focus(selector)
            for char in text:
                await page.keyboard.type(char, delay=random.randint(self.MIN_TYPING_DELAY, self.MAX_TYPING_DELAY))
        except Exception as e:
            print(f"⚠️ DirectBrowser: Typing error (ignoring): {e}")

    async def search(self, query, num_results=10, engine='google'):
        """
        Performs a search using the specified engine (google/ddg).
        """
        print(f"🕵️ DirectBrowser: Searching for '{query}' on {engine.upper()}...")
        
        # Configuration for Engines
        SEARCH_CONFIG = {
            'google': {
                'url': 'https://www.google.com',
                'consent_text': 'Before you continue to Google',
                'input_selector': 'textarea[name="q"], input[name="q"]',
                'input_selector_results': 'textarea[name="q"], input[name="q"]',
                'result_selector': 'div.g', 
                'link_selector': 'a:has(h3)', 
                'snippet_selector': 'div[style*="-webkit-line-clamp"]', # Common Google snippet container
                'next_selector': 'a#pnnext'
            },
            'ddg': {
                'url': 'https://duckduckgo.com',
                'consent_text': '', 
                'input_selector': '#searchbox_input', 
                'input_selector_results': '#search_form_input', 
                'result_selector': 'article',
                'link_selector': 'h2 a', 
                'snippet_selector': 'div.react-results--main', # DDG Snippet
                'next_selector': 'a#more-results'
            }
        }
        
        cfg = SEARCH_CONFIG.get(engine, SEARCH_CONFIG['google'])
        
        results = []
        
        # Calculate pages needed (approx 10 results per page)
        num_pages = (num_results // 10) + 1
        if num_pages > 5: num_pages = 5
        
        # Instantiate BrowserManager
        self.browser_manager = BrowserManager(session_id=self.session_id)
        
        try:
            # Launch with persistence and stealth (and proxy if configured)
            page = await self.browser_manager.launch(headless=self.headless, proxy=self.proxy)
            
            # 1. Navigation
            await page.goto(cfg['url'], wait_until="domcontentloaded")
            
            # Cookie Consent (Google only)
            if engine == 'google':
                try:
                    # Check for consent frame or popup
                    # We can refine this using the saved session -> If saved, we likely won't see this.
                    if await page.get_by_text(cfg['consent_text']).count() > 0:
                        print("🍪 DirectBrowser: Handling Cookies...")
                        reject_btn = page.get_by_role("button", name="Reject all")
                        accept_btn = page.get_by_role("button", name="Accept all")
                        # Also check for "Read more" type popups
                        
                        if await reject_btn.count() > 0: await reject_btn.click()
                        elif await accept_btn.count() > 0: await accept_btn.click()
                        await page.wait_for_load_state("networkidle")
                except: pass

            # 2. Typing
            input_sel = cfg['input_selector']
            try:
                await page.wait_for_selector(input_sel, state="visible", timeout=5000)
            except:
                 input_sel = cfg['input_selector_results'] # Fallback
            
            await self._human_type(page, input_sel, query)
            await page.keyboard.press("Enter")
            
            # 3. Pagination Loop
            for i in range(num_pages):
                await page.wait_for_load_state("networkidle")
                await asyncio.sleep(random.randint(self.MIN_PAGE_DELAY, self.MAX_PAGE_DELAY) / 1000)
                
                # Extract Results - BROAD STRATEGY
                all_links = await page.get_by_role("link").all()
                
                batch_count = 0
                for link_element in all_links:
                    if len(results) >= num_results: break
                    try:
                        url = await link_element.get_attribute('href')
                        if not url: continue
                        
                        # Filter Engine Internal
                        if engine == 'google' and ('google.' in url or not url.startswith('http')): continue
                        if engine == 'ddg':
                            if 'duckduckgo.com' in url or 'spreadprivacy.com' in url: continue
                            if not url.startswith('http'): continue
                            
                        title = await link_element.inner_text()
                        if not title or len(title.strip()) < 5: continue
                        
                        # Snippet Extraction (Attempt)
                        snippet = ""
                        try:
                            # We get the parent 'result container' to find the snippet relative to the link
                            # Google: link is in div.g -> parent
                            parent = link_element.locator("..").locator("..") 
                            if engine == 'google':
                                # Targeted snippet extraction for Google
                                # Try multiple common snippet classes
                                possible_snippets = await parent.locator('div[style*="-webkit-line-clamp"], span.aCOpRe').all_inner_texts()
                                if possible_snippets: snippet = " ".join(possible_snippets)
                                else: snippet = await parent.inner_text() # Fallback to full text
                            else:
                                # DDG
                                snippet = await parent.inner_text()
                        except: pass
                        
                        # Avoid duplicates
                        if any(r['url'] == url for r in results): continue

                        results.append({'title': title.strip(), 'url': url, 'source': engine, 'snippet': snippet})
                        batch_count += 1
                    except: continue
                    
                print(f"   Page {i+1}: Found {batch_count} new results.")
                
                if len(results) >= num_results: break
                
                # Next Page
                if i < num_pages - 1:
                    if engine == 'ddg':
                         # DDG infinite scroll / more button
                         more = page.locator('button#more-results')
                         if await more.is_visible(): await more.click()
                         else: await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    else:
                        # Google
                        nxt = page.locator(cfg['next_selector'])
                        if await nxt.is_visible():
                            await nxt.click()
                        else:
                            break
        
        except Exception as e:
            print(f"❌ DirectBrowser Error: {e}")
        
        finally:
            if self.browser_manager:
                await self.browser_manager.close()
            
        return results

    async def get_page_content(self, url):
        """
        Visits a URL using the stealth browser and returns the HTML content.
        Uses BrowserManager for stealth.
        """
        print(f"🕵️ DirectBrowser: Visiting '{url}'...")
        content = ""
        
        self.browser_manager = BrowserManager(session_id=self.session_id)
        
        try:
            page = await self.browser_manager.launch(headless=self.headless)
            
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            # Small human delay + Random scroll to look active
            await page.mouse.wheel(0, 300)
            await asyncio.sleep(random.randint(2000, 4000) / 1000)
            
            content = await page.content()
            
        except Exception as e:
            print(f"❌ DirectBrowser Visit Error ({url}): {e}")
            
        finally:
            if self.browser_manager:
                await self.browser_manager.close()
                
        return content

