from .base import BaseAgent
from scraper import search_searxng
from extractor import fetch_html, extract_emails_from_site
from social_scraper import SocialScraper
import json
import asyncio
import aiohttp

class ResearcherAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            role="Lead Researcher & Data Gatherer",
            goal="Find relevant leads, gather deep information, and ensure data completeness by self-correcting.",
            provider=provider
        )
        self.footprints = self._load_footprints()
        self.social_scraper = SocialScraper()

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
        
        # Platform Detection
        analyzed = []
        for item in urls:
            url = item['url']
            plat = await self.detect_platform(url)
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

    async def detect_platform(self, url):
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
            async with aiohttp.ClientSession() as session:
                 html = await fetch_html(session, url, timeout=5)
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
            res = await self._perform_search(query, limit=limit)
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

    async def _perform_search(self, query, limit=None):
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
        async with aiohttp.ClientSession() as session:
            # Basic scrape
            html = await fetch_html(session, url)
            emails = await extract_emails_from_site(session, url)
            
            # Self-Correction Logic: Check if we have enough info
            # Simple heuristic: If main page is empty or minimal, we might need to look for specific pages
            
            info = {
                "url": url,
                "html_preview": html[:2000] if html else "", # Truncate for LLM
                "emails": list(emails)
            }
            
            # Ask LLM if we gathered enough info
            instructions = (
                "Analyze the gathered info. Do we have enough to identify the company's business model and a contact point?\n"
                "If not, suggest a specific sub-page to look specifically for (e.g. '/about', '/pricing', '/team').\n"
                "Return JSON: {'complete': bool, 'missing_info': str, 'next_step_url': str or None}"
            )
            
            decision = self.generate_json(f"Gathered Info:\n{info}\n\n{instructions}")
            
            if decision and not decision.get("complete") and decision.get("next_step_url"):
                # "Agentic Loop": Go deeper (one level for now to avoid infinite loops)
                # Ensure the next_step_url is absolute or relative joined
                next_url = decision['next_step_url']
                if not next_url.startswith('http'):
                    next_url = url.rstrip('/') + '/' + next_url.lstrip('/')
                    
                sub_html = await fetch_html(session, next_url)
                info['additional_page'] = next_url
                info['additional_html'] = sub_html[:2000] if sub_html else ""
                
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

    def think(self, context, instructions=None):
        """
        Processes a request. If it looks like a search query, perform the search.
        Otherwise, analyze the provided data.
        """
        # Heuristic: If context is a short string and not JSON/Data, treat as search query
        is_query = False
        if isinstance(context, str) and len(context) < 300:
            is_query = True
            if "{" in context and "}" in context: # vague check for JSON
                is_query = False
        
        if is_query:
            self.logger.info(f"ResearcherAgent received query via think(): {context}")
            print(f"[Researcher] 🔎 Searching for: '{context}'...")
            # Run async gather_intel synchronously
            res = asyncio.run(self.gather_intel({"query": context}))
            print(f"[Researcher] ✅ Found {len(res.get('results', []))} results.")
            return res
        
        # Fallback: Analyze provided data
        prompt = f"Analyze this research data:\n{context}"
        if instructions:
            prompt += f"\n\nAdditional Instructions:\n{instructions}"
        return self.provider.generate_text(prompt)
