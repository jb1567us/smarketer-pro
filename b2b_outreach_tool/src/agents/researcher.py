from .base import BaseAgent
from scraper import search_searxng
from extractor import fetch_html, extract_emails_from_site
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
            
        return analyzed

    async def detect_platform(self, url):
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
            import aiohttp
            async with aiohttp.ClientSession() as session:
                 html = await fetch_html(session, url, timeout=5)
                 if html:
                     if "wp-content" in html or "WordPress" in html: return "WordPress"
                     if "Drupal" in html: return "Drupal"
                     if "Joomla" in html: return "Joomla"
                     if "vBulletin" in html: return "vBulletin"
                     if "xenForo" in html: return "xenForo"
                     if "Shopify" in html: return "Shopify"
        except:
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
                                final_urls.append({"url": e_url, "source_type": "listing"})
                        else:
                            final_urls.append({"url": url, "source_type": "organic"}) # Fallback
                    except Exception as e:
                        print(f"  [Researcher] Error expanding list {url}: {e}")
                        final_urls.append({"url": url, "source_type": "organic"})
                    else:
                        final_urls.append({"url": url, "source_type": "organic"})
            
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
            
            decision = self.provider.generate_json(f"Gathered Info:\n{info}\n\n{instructions}")
            
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
                        f"Sub-page ({path}) HTML:\n{sub_html[:3000]}\n\n"
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

    def think(self, context):
        # The researcher thinks via async gather_intel mostly, 
        # but if we need a synchronous 'opinion' on data, we use this.
        return self.provider.generate_text(f"Analyze this research data:\n{context}")
