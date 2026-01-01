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
            
            # Deduplicate by URL
            unique = {item['url']: item for item in final_urls}.values()
            return {"action": "search_completed", "results": list(unique)}

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

    def think(self, context):
        # The researcher thinks via async gather_intel mostly, 
        # but if we need a synchronous 'opinion' on data, we use this.
        return self.provider.generate_text(f"Analyze this research data:\n{context}")
