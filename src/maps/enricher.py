import asyncio
import os
import csv
import sys
import re
import argparse
from typing import List, Dict

# Ensure src is in path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from playwright.async_api import async_playwright
from playwright_stealth import Stealth

class SiteEnricher:
    """
    Enricher that visits business websites to extract Emails, Socials, Tech Stack, and Contact Names.
    """
    def __init__(self, input_file="data/extracted_businesses.csv", output_file="data/final_leads_enriched.csv", custom1="", custom2=""):
        self.input_file = input_file
        self.output_file = output_file
        self.custom1 = custom1
        self.custom2 = custom2
        self.ensure_output_dir()
        self.output_fields = [
            "business_name", "city", "state", "country", "website", "phone", "emails", "socials", 
            "tech_stack", "contact_names", "tagline", "growth_signals", "proof_assets", 
            "custom_1", "custom_2", "maps_url", "source_url"
        ]

# ... existing code ...



    def ensure_output_dir(self):
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)

    async def run_enrichment(self):
        """
        Main loop: Read extracted businesses -> Visit Website -> Extract Data -> Write.
        """
        if not os.path.exists(self.input_file):
            print(f"❌ Input file not found: {self.input_file}")
            return

        print(f"💎 SiteEnricher: processing {self.input_file}...")
        
        tasks = []
        with open(self.input_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            tasks = list(reader)

        # Output file initialization
        file_exists = os.path.exists(self.output_file)
        if not file_exists:
            with open(self.output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.output_fields)
                writer.writeheader()

        async with async_playwright() as p:
            # Use persistent context to share session/cookies if needed, but mainly for stealth
            user_data_dir = os.path.join(os.getcwd(), 'chrome_profile')
            browser = await p.chromium.launch_persistent_context(
                user_data_dir,
                headless=False, # Visible for now
                channel="chrome",
                ignore_default_args=["--enable-automation"],
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--start-maximized',
                    '--disable-infobars'
                ],
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
                viewport=None
            )
            
            page = browser.pages[0] if browser.pages else await browser.new_page()
            await Stealth().apply_stealth_async(page)
            
            for row in tasks:
                website = row.get("website")
                if not website or "google.com" in website: continue
                
                print(f"\n🌍 Visiting: {website} ...")
                
                enriched_data = row.copy()
                # Aggregate sets
                all_emails = set()
                all_socials = set()
                all_tech = set()
                all_names = set()
                intel_dict = {
                    'tagline': "",
                    'growth_signals': set(),
                    'proof_assets': set()
                }
                
                try:
                    # 1. Visit Homepage
                    await page.goto(website, timeout=30000, wait_until="domcontentloaded")
                    await asyncio.sleep(2)
                    
                    # Scrape Homepage
                    await self._scrape_current_page(page, all_emails, all_socials, all_tech, all_names, intel_dict)
                    
                    # 2. Find Subpages (About, Contact, Team)
                    subpages = await self._find_subpages(page)
                    print(f"    🔗 Found subpages: {subpages}")
                    
                    # 3. Visit Subpages (Limit 2 to save time)
                    for sub_url in subpages[:2]:
                        try:
                            print(f"    Here we go -> {sub_url}")
                            await page.goto(sub_url, timeout=20000, wait_until="domcontentloaded")
                            await asyncio.sleep(1)
                            await self._scrape_current_page(page, all_emails, all_socials, all_tech, all_names, intel_dict)
                        except Exception as e:
                            print(f"      Could not visit {sub_url}: {e}")
                            
                    # Update row
                    enriched_data['emails'] = ", ".join(list(all_emails))
                    enriched_data['socials'] = ", ".join(list(all_socials))
                    enriched_data['tech_stack'] = ", ".join(list(all_tech))
                    enriched_data['contact_names'] = ", ".join(list(all_names))
                    enriched_data['tagline'] = intel_dict['tagline']
                    enriched_data['growth_signals'] = ", ".join(list(intel_dict['growth_signals']))
                    enriched_data['proof_assets'] = ", ".join(list(intel_dict['proof_assets']))
                    
                    # Schema Refinement
                    enriched_data['state'] = row.get("state", "")
                    enriched_data['country'] = row.get("country", "")
                    enriched_data['custom_1'] = self.custom1
                    enriched_data['custom_2'] = self.custom2
                    
                    print(f"    ✅ Final: {len(all_emails)} emails, {len(all_socials)} socials")
                    print(f"       Tagline: {enriched_data['tagline'][:50]}...")
                    print(f"       Growth: {enriched_data['growth_signals']} | Proof: {enriched_data['proof_assets']}")
                    
                except Exception as e:
                    print(f"    ❌ Failed: {e}")
                
                self.save_row(enriched_data)
                
            await browser.close()

    async def _scrape_current_page(self, page, emails_set, socials_set, tech_set, names_set, intel_dict):
        """Helper to scrape data from current open page."""
        try:
            content = await page.content()
            
            # Emails
            found_emails = self.extract_emails(content)
            emails_set.update(found_emails)
            
            # Socials
            found_socials = await self.extract_socials_js(page)
            socials_set.update(found_socials)
            
            # Tech
            found_tech = self.detect_tech_stack(content)
            tech_set.update(found_tech)
            
            # Names
            found_names = await self.find_contact_names(page)
            names_set.update(found_names)
            
            # --- Advanced Intel ---
            # Tagline (Identity) - Only needed once, usually from Home
            if not intel_dict.get('tagline'):
                identity = await self.extract_identity(page)
                if identity:
                    intel_dict['tagline'] = identity
            
            # Growth Signals
            growth = self.detect_growth(content)
            intel_dict['growth_signals'].update(growth)
            
            # Proof Assets
            proof = self.detect_proof(content)
            intel_dict['proof_assets'].update(proof)
            
        except Exception as e:
            print(f"    ⚠️ Scrape error: {e}")

    async def extract_identity(self, page):
        """Extracts Title/H1/Meta as a tagline proxy."""
        try:
            # Priority: Meta Description > H1 > Title
            # Actually, H1 is often the visual tagline. Meta description is the summary.
            
            # Get H1
            h1 = ""
            try:
                h1_el = page.locator("h1").first
                if await h1_el.count() > 0:
                    h1 = await h1_el.inner_text()
                    h1 = h1.strip().replace("\n", " ")
            except: pass
            
            # Get Meta Description
            meta = ""
            try:
                meta_el = page.locator('meta[name="description"]')
                if await meta_el.count() > 0:
                    meta = await meta_el.get_attribute("content")
            except: pass
            
            if meta: return meta[:150] + "..." if len(meta) > 150 else meta
            if h1: return h1
            
            return await page.title()
        except: return ""

    def detect_growth(self, html):
        signals = set()
        lower_html = html.lower()
        if "careers" in lower_html or "join our team" in lower_html:
            signals.add("Hiring Page")
        if "we are hiring" in lower_html:
            signals.add("Active Hiring")
        if "growing team" in lower_html:
            signals.add("Growing Team")
        return list(signals)

    def detect_proof(self, html):
        signals = set()
        lower_html = html.lower()
        if "case stud" in lower_html: # case study, case studies
            signals.add("Case Studies")
        if "testimonial" in lower_html:
            signals.add("Testimonials")
        if "our work" in lower_html or "portfolio" in lower_html:
            signals.add("Portfolio")
        if "client" in lower_html and "logo" in lower_html: # Weak signal but maybe
            pass
        return list(signals)

    async def _find_subpages(self, page):
        """Finds About, Contact, Team links on the current page."""
        try:
            links = await page.evaluate('''() => {
                const anchors = Array.from(document.querySelectorAll('a'));
                const keywords = ['about', 'contact', 'team', 'our story', 'connect'];
                
                return anchors
                    .filter(a => {
                        const text = (a.innerText || "").toLowerCase();
                        return keywords.some(k => text.includes(k));
                    })
                    .map(a => a.href)
                    .filter(href => href.startsWith('http') && !href.includes('#') && !href.includes('mailto'));
            }''')
            
            # Deduplicate and filter external domains (heuristic)
            current_url = page.url
            base_domain = "/".join(current_url.split("/")[:3]) # http://domain.com
            
            filtered = []
            seen = set()
            for l in links:
                if l in seen: continue
                # Keep only internal links usually, or relative
                if base_domain in l:
                    filtered.append(l)
                    seen.add(l)
            return list(seen)
        except:
            return []

    def extract_emails(self, html_content):
        # Basic regex for emails
        # Exclude common image extensions to avoid 'image@2x.png' mistakes
        regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        matches = re.findall(regex, html_content)
        unique = set()
        for m in matches:
            m = m.lower()
            if m.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp')): continue
            if 'sentry' in m or 'u00' in m or 'example' in m: continue
            unique.add(m)
        return list(unique)

    async def extract_socials_js(self, page):
        """
        Extracts social media links using JavaScript to scan all <a> tags.
        """
        try:
            links = await page.evaluate('''() => {
                const anchors = Array.from(document.querySelectorAll('a'));
                const socialDomains = ['instagram.com', 'facebook.com', 'linkedin.com', 'pinterest.com', 'twitter.com', 'x.com', 'tiktok.com'];
                
                return anchors
                    .map(a => a.href)
                    .filter(href => socialDomains.some(d => href.includes(d)))
                    .filter(href => !href.includes('/share') && !href.includes('/sharer')); // Exclude share buttons
            }''')
            return list(set(links))
        except Exception as e:
            print(f"    ⚠️ Social extract error: {e}")
            return []

    # Correction: I will implement extraction methods properly inside run_enrichment or helper
    # combining logic effectively.
    
    def detect_tech_stack(self, html):
        stack = []
        if "/wp-content/" in html: stack.append("WordPress")
        if "shopify" in html.lower(): stack.append("Shopify")
        if "squarespace" in html.lower(): stack.append("Squarespace")
        if "wix.com" in html.lower(): stack.append("Wix")
        if "gtm-" in html or "googletagmanager" in html: stack.append("GTM")
        if "fbevents.js" in html: stack.append("MetaPixel")
        return stack

    async def find_contact_names(self, page):
        # Heuristic: Look for "About" or "Team" link, click it, scan for capitalized names?
        # This is hard. For V1, let's just check the current page (Homepage) for "Hi, I'm [Name]"
        # or "Principal: [Name]"
        
        names = []
        try:
            text = await page.inner_text("body")
            # Look for "Principal", "Founder", "Owner", "Designer" followed by a Name
            # Regex: (Principal|Founder|Owner|Director)\s+([A-Z][a-z]+\s[A-Z][a-z]+)
            patterns = [
                r"(?:Principal|Founder|Owner|Director|Designer)\s+([A-Z][a-z]+\s[A-Z][a-z]+)",
                r"Hi, I'm\s+([A-Z][a-z]+)"
            ]
            for pat in patterns:
                found = re.findall(pat, text)
                names.extend(found)
        except: pass
        return list(set(names))
    
    def save_row(self, row):
        # Safe save only fields we know
        clean_row = {k: row.get(k, "") for k in self.output_fields}
        with open(self.output_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=self.output_fields)
            writer.writerow(clean_row)

    # Helper for socials using regex on content is easier 
    def extract_socials_from_text(self, text):
        socials = set()
        domains = ["instagram.com", "facebook.com", "linkedin.com", "pinterest.com", "twitter.com", "x.com"]
        # Simple Scan
        # This is a bit weak, but better to get specific links from hrefs.
        # I'll update the class logic below to use js eval for hrefs.
        return list(socials)

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        
    parser = argparse.ArgumentParser(description="Enrich Business Leads")
    parser.add_argument("--custom1", type=str, default="", help="Value for custom_1 column")
    parser.add_argument("--custom2", type=str, default="", help="Value for custom_2 column")
    
    args = parser.parse_args()
    
    enricher = SiteEnricher(custom1=args.custom1, custom2=args.custom2)
    asyncio.run(enricher.run_enrichment())


