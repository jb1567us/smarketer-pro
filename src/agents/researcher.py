from .base import BaseAgent
from scraper import search_searxng
from extractor import fetch_html, extract_emails_from_site, extract_emails_from_text
from social_scraper import SocialScraper
import json
import asyncio
import aiohttp
from prompt_engine import PromptEngine, PromptContext

class ResearcherAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            role="Lead Researcher",
            goal="Find relevant leads, gather deep information, and ensure data completeness by self-correcting.",
            backstory=(
                "You are Researcher, a top-tier investigator agent harvested from LOLLMS 'internet/researcher'. "
                "Your core mission is to dive deep into topics, verify facts, and structure data methodically. "
                "You do not just 'google'; you plan your research, cross-reference sources, and synthesize findings "
                "into coherent, cited reports. You are persistent, objective, and thorough."
            ),
            provider=provider
        )
        self.social_scraper = SocialScraper()
        self.captcha_queue = []
        self.prompt_engine = PromptEngine()

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
        
        results = await self._perform_search(footprint, limit=num_results, status_callback=status_callback)
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
            
        self.save_work(analyzed, artifact_type="harvested_urls", metadata={"footprint": footprint})
        return analyzed

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
        Identifies if a site is WordPress, Joomla, Drupal, 4image, etc.
        """
        url_lower = url.lower()
        # Fast URL checks
        if "wp-" in url_lower: return "WordPress"
        if "option=com_" in url_lower: return "Joomla"
        if "node/" in url_lower: return "Drupal"
        if "showthread.php" in url_lower: return "vBulletin"
        if "viewtopic.php" in url_lower: return "phpBB"
        if "4image" in url_lower: return "4image"
        
        signatures = {
            "WordPress": ["wp-content", "wp-includes", "wp-json", "wp-embed", "/wp-"],
            "Joomla": ["/media/system/js/", "index.php?option=com_", "content/view", "joomla-script"],
            "Drupal": ["Drupal.settings", "/sites/all/", "node/add", "drupal.js"],
            "vBulletin": ["vbulletin_global.js", "vbulletin_css", "id=\"vbulletin_html\""],
            "Shopify": ["cdn.shopify.com", "myshopify.com", "shopify-payment-button"],
            "Magento": ["Mage.Cookies", "magento-icon", "skin/frontend", "js/mage"],
            "Wix": ["wix.com", "_wix_", "wix-active-view"],
            "Squarespace": ["squarespace.com", "static1.squarespace.com", "sqs-layout"],
            "Ghost": ["ghost-content", "ghost-sdk", "ghost.org"],
            "XenForo": ["xenforo", "XF.config"],
            "Discuz": ["discuz", "viewthread.php?tid="],
            "phpBB": ["phpbb", "viewtopic.php?f="]
        }
        
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
            query = context["query"]
            if not query or not isinstance(query, str) or not query.strip():
                self.logger.warning(f"Invalid query provided to gather_intel: {query}")
                return {"error": "Invalid query provided", "results": []}
                
            limit = context.get("limit")
            res = await self._perform_search(query, limit=limit, status_callback=lambda m: self.logger.info(m)) # Basic bridge for now
            self.save_work(res, artifact_type="search_results", metadata={"query": query})
            return res
        
        # If context is a URL, scrape and analyze
        if "url" in context:
            # We use enrich_lead_data which calls deep_scrape internally + adds social signals
            self.logger.info(f"Analyzing URL with Social Scout: {context['url']}")
            res = await self.enrich_lead_data(context["url"])
            self.save_work(res, artifact_type="enriched_lead_data", metadata={"url": context["url"]})
            return res

        return {"error": "No query or URL provided in context"}

    async def _perform_search(self, query, limit=None, status_callback=None):
        from .list_parser import ListParser
        from config import config
        list_parser = ListParser()
        
        if not limit:
            limit = config['search'].get('max_results', 50)
        
        # Load default profile engines/categories to ensure we use Bing (Resilience)
        # instead of failing on Google defaults
        profile = config['search']['profiles'].get('default', {})
        engines = profile.get('engines')
        categories = profile.get('categories')

        async with aiohttp.ClientSession() as session:
            # Ralph-Style Discovery: Retry with broadening if results are empty
            max_retries = 2
            for attempt in range(max_retries + 1):
                msg = f"  [Discovery] Searching for: '{query}' (Attempt {attempt+1})"
                self.logger.info(msg)
                if status_callback: status_callback(msg)
                raw_results = await search_searxng(
                    query, 
                    session, 
                    num_results=limit,
                    categories=categories,
                    engines=engines
                )
                
                if raw_results:
                    break
                    
                if attempt < max_retries:
                    msg = f"  ⚠️ No results for '{query}'. Broadening search keywords..."
                    self.logger.info(msg)
                    if status_callback: status_callback(msg)
                    # Ask LLM to broaden the query
                    broaden_prompt = (
                        f"The search query '{query}' returned 0 results. "
                        f"Suggest a broader, similar search query that would find relevant B2B leads in the same niche. "
                        f"Keep it to a single search phrase. Return ONLY the new query string."
                    )
                    new_query = self.provider.generate_text(broaden_prompt).strip().strip('"').strip("'")
                    if new_query and new_query.lower() != query.lower():
                        query = new_query
                    else:
                        break # Give up if LLM fails to provide a new query
                else:
                    self.logger.warning(f"  ❌ No results found after broadening.")
                    return {"action": "search_failed", "results": [], "reason": "No results after broadening"}
            
            final_urls = []
            
            for res in raw_results:
                url = res['url']
                title = res['title']
                
                # Preserving metadata
                meta = {"title": title, "snippet": res.get("snippet", "")}

                if list_parser.is_listicle(title, url):
                    self.logger.info(f"Detected Aggregator/List: {title} ({url})")
                    self.logger.debug("Expanding list to find direct business links...")
                    try:
                        html = await fetch_html(session, url)
                        if html:
                            extracted = list_parser.extract_external_links(html, url, [])
                            self.logger.info(f"Extracted {len(extracted)} potential business links from list.")
                            # Mark as high-quality "listing" leads
                            for e_url in extracted:
                                final_urls.append({"url": e_url, "source_type": "listing", **meta})
                        else:
                            final_urls.append({"url": url, "source_type": "organic", **meta}) # Fallback
                    except Exception as e:
                        self.logger.error(f"Error expanding list {url}: {e}", exc_info=True)
                        final_urls.append({"url": url, "source_type": "organic", **meta})
                else:
                     final_urls.append({"url": url, "source_type": "organic", **meta})
            
            # Deduplicate by URL and cap to limit
            unique = {item['url']: item for item in final_urls}.values()
            results = list(unique)[:limit]
            return {"action": "search_completed", "results": results}

    async def _deep_scrape(self, url):
        """Alpha Ralph-Style: Scrapes homepage and automatically scouts for contact/about pages if needed."""
        async with aiohttp.ClientSession() as session:
            # 1. Homepage Scrape
            html = await fetch_html(session, url)
            
            if html == "__CAPTCHA_BLOCKED__":
                self.logger.warning(f"  [Scraper] Captcha detected on {url}. Adding to healing queue.")
                self.captcha_queue.append(url)
                return {"url": url, "status": "captcha_blocked", "emails": []}

            emails = await extract_emails_from_site(session, url) if html else set()
            
            info = {
                "url": url,
                "html_preview": html[:2000] if html else "",
                "emails": list(emails)
            }
            
            # 2. Heuristic Check: If no email found, try specific strategy rotation
            if not emails and html:
                self.logger.info(f"  [Scraper] No emails on homepage of {url}. Triggering scout loop...")
                scout_paths = ["/contact", "/about", "/contact-us", "/about-us"]
                for path in scout_paths:
                    scout_url = url.rstrip('/') + path
                    self.logger.debug(f"    Scouting: {scout_url}")
                    s_html = await fetch_html(session, scout_url)
                    
                    if s_html == "__CAPTCHA_BLOCKED__":
                         self.logger.warning(f"    [Scraper] Captcha detected on sub-page {scout_url}. Queuing.")
                         self.captcha_queue.append(scout_url)
                         continue

                    if s_html:
                        s_emails = extract_emails_from_text(s_html)
                        if s_emails:
                            self.logger.info(f"    ✅ Success! Found {len(s_emails)} emails on {path}")
                            emails.update(s_emails)
                            info['emails'] = list(emails)
                            break # Found some, good enough for now
            
            # 3. LLM-based Strategy Correction
            instructions = (
                "Analyze the gathered info. Do we have enough to identify the company's business model and a contact point?\n"
                "If not, suggest a specific sub-page to look specifically for (e.g. '/pricing', '/team', '/legal').\n"
                "Return JSON: {'complete': bool, 'missing_info': str, 'next_step_url': str or None}"
            )
            
            decision = self.generate_json(f"Gathered Info:\n{info}\n\n{instructions}")
            
            if decision and not decision.get("complete") and decision.get("next_step_url"):
                self.logger.info(f"  [Scraper] Ralph Recommendation: Scouting {decision['next_step_url']}")
                next_url = decision['next_step_url']
                if not next_url.startswith('http'):
                    next_url = url.rstrip('/') + '/' + next_url.lstrip('/')
                    
                sub_html = await fetch_html(session, next_url)
                if sub_html == "__CAPTCHA_BLOCKED__":
                    self.captcha_queue.append(next_url)
                elif sub_html:
                    info['additional_page'] = next_url
                    info['additional_html'] = sub_html[:2000]
                    # One last email grab
                    emails.update(extract_emails_from_text(sub_html))
                    info['emails'] = list(emails)
                
            return info

    async def process_captcha_queue(self):
        """
        Ralph-Style 'Healing' Loop: 
        Uses a real browser (Playwright) to bypass captchas for blocked leads.
        """
        if not self.captcha_queue:
            return []

        self.logger.info(f"🚀 Starting Captcha Healing Loop for {len(self.captcha_queue)} URLs...")
        
        from utils.browser_manager import BrowserManager
        bm = BrowserManager(session_id="captcha_healing")
        
        healed_data = []
        try:
            # We use headless=False because some captcha solvers/detectors work better with a head
            await bm.launch(headless=True) 
            
            for url in self.captcha_queue:
                self.logger.info(f"  [Healer] Navigating to blocked URL: {url}")
                await bm.page.goto(url, wait_until="networkidle", timeout=30000)
                
                # Check for captcha and solve
                solved = await bm.solve_captcha_if_present()
                if solved:
                    self.logger.info(f"  ✅ Captcha Solved! Capturing content...")
                    # Wait for redirect/load after solving
                    await bm.page.wait_for_timeout(3000)
                    content = await bm.page.content()
                    
                    # Extract emails from the "healed" content
                    emails = extract_emails_from_text(content)
                    
                    res = {
                        "url": url,
                        "status": "healed",
                        "html_preview": content[:3000],
                        "emails": list(emails)
                    }
                    healed_data.append(res)
                else:
                    self.logger.warning(f"  ❌ Could not solve captcha for {url}")
                    
        except Exception as e:
            self.logger.error(f"  [Healer] Error during healing loop: {e}")
        finally:
            await bm.close()
            self.captcha_queue = [] # Clear queue after processing
            
        return healed_data

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
            
            # Truncate HTML to save tokens but keep enough for meta/links
            preview = html[:6000] if html else "No HTML found"
            res = self.generate_json(f"HTML Content:\n{preview}\n\n{extraction_prompt}")
            
            if not res:
                res = {}

            # 3. Deep Dive: Check /about and /careers for richer signals
            sub_pages = ["/about", "/careers", "/about-us", "/blog"]
            all_signals = res.get('intent_signals') or []
            
            for path in sub_pages:
                sub_url = url.rstrip('/') + path
                self.logger.debug(f"Scouting sub-page: {sub_url}")
                sub_html = await fetch_html(session, sub_url)
                if sub_html:
                    c_res = self.generate_json(
                        f"Sub-page ({path}) HTML:\n{sub_html[:3000]}\n\n"
                        "Extract any business intent signals (hiring, product launches, expansion, case studies) as a JSON list. Return [] if none.",
                        expect_list=True
                    )
                    if isinstance(c_res, list):
                        all_signals.extend(c_res)
            
            # Deduplicate signals - handles both strings and dicts
            seen = set()
            unique_signals = []
            for sig in all_signals:
                if isinstance(sig, dict):
                    # Convert dict to a stable string representation for hashing
                    sig_hash = json.dumps(sig, sort_keys=True)
                else:
                    sig_hash = str(sig)
                
                if sig_hash not in seen:
                    seen.add(sig_hash)
                    unique_signals.append(sig)
            
            res['intent_signals'] = unique_signals

            # 4. Metadata Integration (Required by workflow engine)
            res['emails'] = list(await extract_emails_from_site(session, url))
            res['html_preview'] = html[:5000] if html else "" # Provide preview for analyzer/qualifier

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
        Uses SocialScraper to get real data (Bridge API -> Dork -> Browser).
        """
        self.logger.debug(f"Scouting social activity: {social_url}")
        
        # 1. Detect platform from URL
        platform = self.social_scraper._detect_platform(social_url)
        if not platform:
            return None

        # 2. Smart Scrape
        data = await self.social_scraper.smart_scrape(social_url, platform)
        
        if not data or "error" in data:
            return None
            
        # 3. Summarize for Context
        # If we got a feed (Bridge)
        if "posts" in data:
            posts = data["posts"]
            summary = f"Found {len(posts)} recent posts via {data['source']}.\n"
            summary += "Latest topics:\n"
            for p in posts[:3]:
                summary += f" - {p['date']}: {p['title']} ({p['link']})\n"
            return summary
            
        # If we got a browser dump
        if "raw_text_preview" in data:
            # We let the LLM parse this text later or just return a snippet
            return f"Scraped profile via Browser. Preview: {data['raw_text_preview'][:300]}..."
            
        # If we got search results
        if "results" in data:
            return f"Found {len(data['results'])} indexed pages/mentions."
            
        return "Social data found but format unrecognized."

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
