from .base import BaseAgent
from scraper import search_searxng
from social_scraper import SocialScraper
from extractor import fetch_html, extract_emails_from_site, is_captcha
import json
import asyncio
import aiohttp
from prompt_engine import PromptEngine, PromptContext

class ResearcherAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            role="Lead Researcher & Data Gatherer",
            goal="Find relevant leads, gather deep information, and ensure data completeness by self-correcting.",
            provider=provider
        )
        self.social_scraper = SocialScraper()
        self.captcha_queue = []
        self.prompt_engine = PromptEngine()

    def _clean_html_for_llm(self, html, limit=2000):
        """Strips scripts/styles and truncates to avoid 413 Payload Too Large."""
        if not html: return ""
        import re
        # Strip style and script tags
        html = re.sub(r'<(style|script)[^>]*>.*?</\1>', '', html, flags=re.DOTALL)
        # Strip comments
        html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
        # Collapse whitespace
        html = re.sub(r'\s+', ' ', html).strip()
        return html[:limit]

    def generate_discovery_queries(self, icp, offering, constraints):
        """
        Generates high-precision search queries based on ICP.
        """
        prompt = self.prompt_engine.get_prompt(
            "researcher/discovery_query_generator.j2",
            self.kernel if hasattr(self, 'kernel') else PromptContext(niche="General", icp_role="Researcher"),
            icp=icp,
            offering=offering,
            constraints=constraints
        )
        if prompt.startswith("ERROR"):
            self.logger.error(f"Render Error: {prompt}")
            return {"query_groups": [], "error": prompt}
        return self.generate_json(prompt)

    async def generate_discovery_queries_async(self, icp, offering, constraints):
        """
        Async version of generate_discovery_queries.
        """
        prompt = self.prompt_engine.get_prompt(
            "researcher/discovery_query_generator.j2",
            self.kernel if hasattr(self, 'kernel') else PromptContext(niche="General", icp_role="Researcher"),
            icp=icp,
            offering=offering,
            constraints=constraints
        )
        if prompt.startswith("ERROR"):
            self.logger.error(f"Render Error: {prompt}")
            return {"query_groups": [], "error": prompt}
        return await self.generate_json_async(prompt)

    def plan_page_targeting(self, icp, candidate, pages_seen):
        """
        Recommends which URLs to fetch next from the same domain.
        """
        prompt = self.prompt_engine.get_prompt(
            "researcher/page_targeting_planner.j2",
            self.kernel if hasattr(self, 'kernel') else PromptContext(niche="General", icp_role="Researcher"),
            icp=icp,
            candidate=candidate,
            pages_seen=pages_seen
        )
        if prompt.startswith("ERROR"):
            self.logger.error(f"Render Error: {prompt}")
            return {"targets": [], "error": prompt}
        return self.generate_json(prompt)

    async def extract_lead_signals(self, icp, candidate, pages):
        """
        Extracts structured signals from provided page text.
        """
        prompt = self.prompt_engine.get_prompt(
            "researcher/lead_signal_extractor.j2",
            self.kernel if hasattr(self, 'kernel') else PromptContext(niche="General", icp_role="Researcher"),
            icp=icp,
            candidate=candidate,
            pages=pages
        )
        if prompt.startswith("ERROR"):
            self.logger.error(f"Render Error: {prompt}")
            return {"signals": {}, "error": prompt}
        return await self.generate_json_async(prompt)

    def _load_footprints(self):
        """Loads Hrefer-style footprints from JSON."""
        import os
        path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "footprints.json")
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception as e:
            self.logger.warning(f"Could not load footprints: {e}")
            return {}

    async def mass_harvest(self, footprint, num_results=100, status_callback=None):
        """
        ScrapeBox-style harvester: Finds URLs matching a specific footprint.
        """
        if status_callback: status_callback(f"🚀 Starting Mass Harvest for: '{footprint}'")
        
        # Use existing search logic but purely for URL extraction
        # We increase valid engines for mass data
        from config import config
        profile = config['search']['profiles'].get('default', {})
        engines = profile.get('engines', ['google', 'bing', 'yahoo'])
        
        results = await self._perform_search(footprint, limit=num_results)
        urls = results.get("results", [])
        
        if status_callback: status_callback(f"✅ Harvested {len(urls)} raw URLs. Analyzing platforms...")
        
        # Platform Detection (Parallelized)
        analyzed = []
        async with aiohttp.ClientSession() as session:
            tasks = []
            for item in urls:
                tasks.append(self.detect_platform(item['url'], session=session))
            
            platforms = await asyncio.gather(*tasks)
            
            for item, plat in zip(urls, platforms):
                item['platform'] = plat
                analyzed.append(item)
            
        return analyzed

    async def process_search_results(self, results):
        """
        Iterates through search results, visits each page using DirectBrowser, 
        and extracts detailed info (emails, tech stack, etc).
        """
        from search_providers.direct_browser import DirectBrowser
        from extractor import extract_emails_from_text
        
        # Use headless browser for scraping to match search stealth
        browser = DirectBrowser(headless=True)
        
        enriched_leads = []
        
        for item in results:
            url = item.get('url')
            if not url: continue
            
            print(f"  [Researcher] 🔬 Deep Diving: {url}...")
            try:
                # 1. Fetch Content via Stealth Browser
                html_content = await browser.get_page_content(url)
                
                if not html_content:
                    print(f"  [Researcher] ⚠️ Failed to fetch content for {url}")
                    continue
                
                # 2. Extract Signals
                text_content = self._clean_html_for_llm(html_content, limit=20000)
                
                # Basic Extraction (Regex)
                emails = extract_emails_from_text(text_content)
                
                # Store
                item['details'] = {
                    "emails": list(emails),
                    "scraped_text_preview": text_content[:500],
                    "status": "scraped"
                }
                enriched_leads.append(item)
                
            except Exception as e:
                print(f"  [Researcher] Error processing {url}: {e}")
                item['details'] = {"error": str(e)}
                enriched_leads.append(item)
                
        return enriched_leads

    async def keyword_discovery(self, seeds, levels=1, sources=['google'], append_variants=False):
        """
        ScrapeBox-style Keyword Harvester. 
        Takes seed keywords and drills down into suggestions.
        """
        if isinstance(seeds, str): seeds = [seeds]
        
        from scraper import get_keyword_suggestions
        
        discovered = set(seeds)
        current_batch = set(seeds)
        
        async with aiohttp.ClientSession() as session:
            for level in range(levels):
                self.logger.info(f"Suggestion Level {level+1}/{levels}...")
                next_batch = set()
                
                tasks = []
                for kw in current_batch:
                    # Append A-Z if requested
                    variants = [kw]
                    if append_variants:
                        variants.extend([f"{kw} {char}" for char in "abcdefghijklmnopqrstuvwxyz0123456789"])
                    
                    for v in variants:
                        for src in sources:
                            tasks.append(get_keyword_suggestions(v, session, source=src))
                
                results = await asyncio.gather(*tasks)
                for r_list in results:
                    for item in r_list:
                        if item not in discovered:
                            discovered.add(item)
                            next_batch.add(item)
                            
                current_batch = next_batch
                if not current_batch: break
        
        results = sorted(list(discovered))
        self.save_work(results, artifact_type="keyword_list", metadata={"seeds": seeds})
        return results

    async def detect_platform(self, url, session=None):
        """
        Identifies if a site is WordPress, Drupal, Joomla, etc. without full scrape if possible.
        """
        # Simple heuristic based on URL structure or fast HEAD request
        # For full accuracy we need HTML, but let's try URL patterns first
        url_lower = url.lower()
        if "wp-" in url_lower or "/category/" in url_lower:
            return "WordPress"
        if "option=com_" in url_lower:
            return "Joomla"
        if "node/" in url_lower:
            return "Drupal"
        if "showthread.php" in url_lower or "viewtopic.php" in url_lower:
            return "Forum (General)"
            
        # Fallback: check HTML (async)
        # We reuse the fetch_html from extractor but keep it light
        try:
            from extractor import fetch_html
            
            # Use provided session or create a temp one
            if session:
                html = await fetch_html(session, url, timeout=5)
                if html:
                     for platform, markers in signatures.items():
                         if any(marker in html for marker in markers):
                             return platform
            else:
                async with aiohttp.ClientSession() as temp_session:
                     html = await fetch_html(temp_session, url, timeout=5)
                     if html:
                         for platform, markers in signatures.items():
                             if any(marker in html for marker in markers):
                                 return platform

        except Exception as e:
            self.logger.debug(f"Platform detection failed: {e}")
            pass
            
        return "Unknown"

    async def gather_intel(self, context):
        """
        Context can be a 'query' (string) or a 'url' (string).
        """
        # If context is a query, search first
        if "query" in context:
            limit = context.get("limit")
            return await self._perform_search(context["query"], limit=limit)
        
        # If context is a URL, scrape and analyze
        if "url" in context:
            return await self._deep_scrape(context["url"])

        return {"error": "No query or URL provided in context"}

    async def _perform_search(self, query, limit=None):
        from .list_parser import ListParser
        from config import config
        list_parser = ListParser()
        
        if not limit:
            limit = config['search'].get('max_results', 50)
        
        # [DISABLED] Legacy engine loading (DirectBrowser handles this)
        # profile = config['search']['profiles'].get('default', {})
        # engines = profile.get('engines')
        # categories = profile.get('categories')

        async with aiohttp.ClientSession() as session:
            raw_results = await search_searxng(
                query, 
                session, 
                num_results=limit,
                categories=categories,
                engines=engines
            )
            
            final_urls = []
            
            for res in raw_results:
                url = res['url']
                title = res['title']
                
                # Preserving metadata
                meta = {"title": title, "snippet": res.get("snippet", "")}

                if list_parser.is_listicle(title, url):
                    print(f"  [Researcher] Detected Aggregator/List: {title} ({url})")
                    print(f"  [Researcher] Expanding list to find direct business links...")
                    try:
                        html = await fetch_html(session, url)
                        if html:
                            extracted = list_parser.extract_external_links(html, url, [])
                            print(f"  [Researcher] Extracted {len(extracted)} potential business links from list.")
                            # Mark as high-quality "listing" leads
                            for e_url in extracted:
                                final_urls.append({"url": e_url, "source_type": "listing", **meta})
                        else:
                            final_urls.append({"url": url, "source_type": "organic", **meta}) # Fallback
                    except Exception as e:
                        print(f"  [Researcher] Error expanding list {url}: {e}")
                        final_urls.append({"url": url, "source_type": "organic", **meta})
                else:
                     final_urls.append({"url": url, "source_type": "organic", **meta})
            
            # Deduplicate by URL and cap to limit
            unique = {item['url']: item for item in final_urls}.values()
            results = list(unique)[:limit]
            return {"action": "search_completed", "results": results}

    async def _deep_scrape(self, url):
        async with aiohttp.ClientSession() as session:
            # Basic scrape
            html = await fetch_html(session, url)
            
            # CAPTCHA DETECTION
            if is_captcha(html):
                self.logger.warning(f"  [Researcher] Captcha detected at {url}. Queueing for healing.")
                self.add_to_captcha_queue(url, html)
                return {"url": url, "html_preview": html[:500], "captcha": True, "emails": []}

            emails = await extract_emails_from_site(session, url)
            
            # Self-Correction Logic: Check if we have enough info
            # Simple heuristic: If main page is empty or minimal, we might need to look for specific pages
            
            info = {
                "url": url,
                "html_preview": self._clean_html_for_llm(html, limit=1000), 
                "emails": list(emails)
            }
            
            # Ask LLM if we gathered enough info
            instructions = (
                "Analyze the gathered info. Do we have enough to identify the company's business model and a contact point?\n"
                "If not, suggest a specific sub-page to look specifically for (e.g. '/about', '/pricing', '/team').\n"
                "Return JSON: {'complete': bool, 'missing_info': str, 'next_step_url': str or None}"
            )
            
            decision = self.provider.generate_json(f"Gathered Info:\n{info}\n\n{instructions}")
            
            if decision and not decision.get("complete") and decision.get("next_step_url"):
                # "Agentic Loop": Go deeper (one level for now to avoid infinite loops)
                # Ensure the next_step_url is absolute or relative joined
                next_url = decision['next_step_url']
                if not next_url.startswith('http'):
                    next_url = url.rstrip('/') + '/' + next_url.lstrip('/')
                    
                sub_html = await fetch_html(session, next_url)
                info['additional_page'] = next_url
                info['additional_html'] = self._clean_html_for_llm(sub_html, limit=1500)
                
            return info

    async def enrich_lead_data(self, url):
        """
        Deeper intelligence gathering: Social links, Intent signals, Bio, and Technographics.
        """
        async with aiohttp.ClientSession() as session:
            # 1. Scrape Homepage
            html = await fetch_html(session, url)
            
            # 2. Extract Social Links & Basic Meta via LLM parse of the HTML
            extraction_prompt = (
                f"You are a master researcher. Extract the following from the HTML of '{url}':\n"
                "1. Social Media URLs (LinkedIn, Twitter, Instagram)\n"
                "2. 'Intent Signals': Look for phrases like 'We are hiring', 'Just launched', 'Now in [City]', 'Check our latest case study'.\n"
                "3. A 2-sentence company bio.\n"
                "4. 'Technographics': Identify the tech stack used (e.g., Shopify, HubSpot, Wordpress, Intercom, Facebook Pixel) based on code signatures.\n\n"
                "Return JSON ONLY: {\n"
                "  'linkedin_url': str or null,\n"
                "  'twitter_url': str or null,\n"
                "  'instagram_url': str or null,\n"
                "  'intent_signals': list or null,\n"
                "  'company_bio': str or null,\n"
                "  'technographics': list or null\n"
                "}"
            )
            
            # Clean and truncate HTML to save tokens but keep enough for meta/links
            preview = self._clean_html_for_llm(html, limit=2500)
            res = self.provider.generate_json(f"HTML Content:\n{preview}\n\n{extraction_prompt}")
            
            if not res:
                res = {}

            # 3. Deep Dive: Check /about and /careers for richer signals
            sub_pages = ["/about", "/careers", "/about-us", "/blog"]
            all_signals = res.get('intent_signals') or []
            
            for path in sub_pages:
                sub_url = url.rstrip('/') + path
                print(f"  [Researcher] scouting sub-page: {sub_url}")
                sub_html = await fetch_html(session, sub_url)
                if sub_html:
                    c_res = self.provider.generate_json(
                        f"Sub-page ({path}) HTML:\n{self._clean_html_for_llm(sub_html, limit=1000)}\n\n"
                        "Extract any business intent signals (hiring, product launches, expansion, case studies) as a JSON list. Return [] if none."
                    )
                    if isinstance(c_res, list):
                        all_signals.extend(c_res)
            
            # Deduplicate signals
            res['intent_signals'] = list(set(all_signals))

            # Add technographics to intent or as a separate field if needed for DB
            # For now we'll merge them or keep them in the dict as is.

            # 4. Social Scouting (Basic)
            if res.get('linkedin_url'):
                social_data = await self.scout_social_signals(res['linkedin_url'])
                if social_data:
                    res['social_intel'] = social_data

            return res


    async def scout_social_signals(self, social_url):
        """
        Attempts to find recent activity or bio from a social URL.
        Note: Real social scraping is throttled; this simulates/uses public previews if available.
        """
        print(f"  [Researcher] Scouting social activity: {social_url}")
        # In a real-world scenario, we might use Playwright or a social API here.
        # For this MVP, we use the LLM to hypothesize 'Standard Profile Highlights' 
        # based on context if we were able to fetch a preview, or just return placeholder.
        return "Recent activity detected (Simulated): Active in B2B Tech discussions."

    async def think_async(self, context, instructions=None):
        """
        Async version of think with robust intent routing.
        """
        input_text = str(context).lower()
        
        # INTENT: Topic/Keyword Research
        if "topic" in input_text or "keyword" in input_text or "ideas" in input_text:
            self.logger.info("⚡ RESEARCHER: Detected intent -> KEYWORD DISCOVERY")
            # Convert context to seed list
            # Simple extraction: just use the context as the seed phrase
            seeds = [context]
            if isinstance(context, dict) and "query" in context:
                seeds = [context["query"]]
            
            self.logger.info(f"   Running keyword discovery for: {seeds}")
            results = await self.keyword_discovery(seeds, levels=1, sources=['google', 'bing'])
            return f"Ranked Research Topics:\n" + "\n".join([f"- {r}" for r in results[:10]])

        # INTENT: Competitor/Lead Research
        if "competitor" in input_text or "leads" in input_text or "companies" in input_text:
            self.logger.info("⚡ RESEARCHER: Detected intent -> MASS HARVEST")
            footprint = context
            if isinstance(context, dict): footprint = context.get('query', context)
            
            results = await self.mass_harvest(footprint, num_results=10)
            return results

        # DEFAULT: General Intelligence / Search
        self.logger.info("researcher: Defaulting to General Search/Intel Gathering")
        if isinstance(context, str) and len(context) < 300 and "{" not in context:
             return await self.gather_intel({"query": context})
        
        return await self.gather_intel(context if isinstance(context, dict) else {"query": str(context)})

    def think(self, context, instructions=None):
        """
        Processes a request. Checks for loop to allow safe async execution.
        """
        # CHECK FOR RUNNING LOOP to avoid RuntimeError
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            self.logger.warning("think() called from running loop! Use think_async() for best results.")
            # We cannot block here. We must return a coroutine or fail.
            # Ideally, we refactor the caller.
            # For now, we return a 'promise' message if we can't await.
            return {"error": "Async context detected. Please await agent.think_async() instead."}
        else:
            # No loop, safe to run sync
            return asyncio.run(self.think_async(context, instructions))

    async def process_captcha_queue(self):
        """
        Attempts to solve any captchas currently in the queue.
        Returns a list of 'healed' results.
        """
        if not self.captcha_queue:
            return []
            
        self.logger.info(f"💠 Researcher: Processing {len(self.captcha_queue)} items in Captcha Queue...")
        healed = []
        
        import time
        from config import config
        from utils.captcha_solver import CaptchaSolver
        
        solver_cfg = config.get('captcha', {})
        solver = CaptchaSolver(solver_cfg.get('provider', 'none'), solver_cfg.get('api_key'))
        
        items = list(self.captcha_queue)
        self.captcha_queue = []
        
        for item in items:
            self.logger.warning(f"  [Captcha] Attempting healing for: {item.get('url')}")
            # For now, we simulate/placeholder the actual solve since it requires browser/session logic
            # but we return the item so the workflow can at least see it was 'processed'.
            # A full implementation would use 'solver' here.
            healed.append(item)
            
        return healed

    def add_to_captcha_queue(self, url, html_content):
        """Adds a candidate to the captcha queue for later healing."""
        import time
        self.captcha_queue.append({
            "url": url,
            "html_preview": html_content[:5000] if html_content else "",
            "timestamp": time.time()
        })

