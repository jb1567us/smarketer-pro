import reflex as rx
import asyncio
from .base import BaseState, DB_AVAILABLE

class ToolsState(BaseState):
    """Search and Mass Tools state."""
    # Direct Search
    search_query: str = ""
    search_pages: int = 1
    search_results_count: int = 0
    is_searching: bool = False
    
    # Mass Harvester
    mass_tools_keywords: str = ""
    is_harvesting: bool = False
    mass_harvest_results: list[dict] = []
    harvest_limit: int = 50
    
    # Footprint Scraper
    footprint_keywords: str = ""
    is_scraping_footprints: bool = False
    
    # Commenter
    comment_template: str = ""
    comment_target_urls: str = ""
    is_commenting: bool = False

    # Proxy Lab
    proxy_stats_elite: int = 0
    proxy_stats_total: int = 0
    proxy_import_text: str = ""
    is_importing_proxies: bool = False

    # UI State
    tool_type: str = "Mass Harvester"

    def set_tool(self, tool_name: str):
        self.tool_type = tool_name
        self.add_log(f"Switched to tool: {tool_name}")

    def set_harvest_limit(self, limit: str):
        """Set harvest limit from string input."""
        try:
            self.harvest_limit = int(float(limit))
        except (ValueError, TypeError):
            pass

    async def _safe_len(self, results_obj):
        """Helper to safely get length of results, awaiting if it is a coroutine."""
        if results_obj is None:
            return 0
        if asyncio.iscoroutine(results_obj):
            results_obj = await results_obj
        if hasattr(results_obj, "__await__") and not isinstance(results_obj, list):
            results_obj = await results_obj
        return len(results_obj) if results_obj is not None else 0

    async def run_direct_search(self):
        self.is_searching = True
        self.add_log(f"Starting direct search for: {self.search_query}")
        yield
        try:
            from backend.direct_scraper import run_search
            # Execute search and safely get count
            res_obj = run_search(self.search_query, self.search_pages)
            self.search_results_count = await self._safe_len(res_obj)
            self.add_log(f"Found {self.search_results_count} results.")
        except Exception as e:
            self.handle_error(e, "Direct Search")
        finally:
            self.is_searching = False
            yield

    async def run_mass_harvest(self):
        """Run bulk lead harvesting."""
        if not self.mass_tools_keywords: return
        self.is_harvesting = True
        self.add_log("Starting Mass Harvest...")
        yield
        from backend.global_search_harvester import GlobalSearchHarvester
        from backend.extractor import extract_emails_from_site
        import aiohttp
        
        # Parse keywords into queries
        queries = [{"query": k.strip()} for k in self.mass_tools_keywords.split(",") if k.strip()]
        if not queries:
            self.add_log("No valid keywords found.")
            self.is_harvesting = False
            yield
            return

        harvester = GlobalSearchHarvester(input_data=queries)
        raw_results = await harvester.run()
        
        results_count = await self._safe_len(raw_results)
        self.add_log(f"Search complete. Found {results_count} results. Enriching first 10 with contact info...")
        yield
        
        # Enrichment Loop (Parallel)
        async with aiohttp.ClientSession() as session:
            final_results = []
            # Concurrency limit for enrichment
            sem = asyncio.Semaphore(5)
            
            async def enrich(res):
                async with sem:
                    url = res.get('url')
                    if url:
                        try:
                            # Attempt to extract emails
                            emails = await extract_emails_from_site(session, url)
                            res['email'] = ", ".join(emails) if emails else "No email found"
                        except Exception:
                            res['email'] = "Extraction failed"
                    else:
                        res['email'] = "N/A"
                    return res
            
            # Enrich first 10 results to keep it responsive for the user
            enrich_tasks = [enrich(res) for res in raw_results[:10]]
            enriched = await asyncio.gather(*enrich_tasks)
            
            # Combine enriched results with the rest
            final_results = list(enriched)
            if len(raw_results) > 10:
                for res in raw_results[10:]:
                    res['email'] = "[Run Enrichment separately for more]"
                    final_results.append(res)
                    
            self.mass_harvest_results = final_results
            
        self.is_harvesting = False
        self.add_log(f"Mass Harvest complete. Found {len(self.mass_harvest_results)} leads.")
        yield

    async def run_footprint_scrape(self):
        """Scrape targets using footprints."""
        if not self.footprint_keywords: return
        self.is_scraping_footprints = True
        self.add_log("Starting Footprint Scrape...")
        yield
        
        from backend.global_search_harvester import GlobalSearchHarvester
        # Footprint queries usually look like site:instagram.com "keyword"
        queries = [{"query": k.strip()} for k in self.footprint_keywords.split(",") if k.strip()]
        if not queries:
            self.add_log("No valid footprints found.")
            self.is_scraping_footprints = False
            yield
            return

        harvester = GlobalSearchHarvester(input_data=queries)
        results = await harvester.run()
        
        self.is_scraping_footprints = False
        self.add_log(f"Footprint Scrape complete. Found {len(results)} potential targets.")
        yield

    async def run_mass_comment(self):
        """Run automated commenting."""
        if not self.comment_target_urls: return
        self.is_commenting = True
        self.add_log("Starting Mass Commenting...")
        yield
        
        from backend.agents.comment_agent import CommentAgent
        agent = CommentAgent()
        
        urls = [u.strip() for u in self.comment_target_urls.split(",") if u.strip()]
        success_count = 0
        
        for url in urls:
            self.add_log(f"Commenting on {url}...")
            # Use defaults or template data
            res = await agent.post_comment(
                target_url=url,
                name="Research Bot", 
                email="bot@outreach.internal",
                website="https://outreach-proto.web.app",
                comment_body=self.comment_template or "Excellent insights. Added to my research feed."
            )
            if res.get('status') == 'success':
                success_count += 1
                self.add_log(f"✅ Comment posted to {url}")
            else:
                self.add_log(f"❌ Failed on {url}: {res.get('reason')}")
            yield
            
        self.is_commenting = False
        self.add_log(f"Mass Commenting complete. Success: {success_count}/{len(urls)}")
        yield

    async def import_proxies_now(self):
        """Import proxies from text input."""
        if not self.proxy_import_text: return
        self.is_importing_proxies = True
        self.add_log(f"Importing proxies...")
        yield
        
        from backend.proxy_manager import proxy_manager
        from backend.database import get_best_proxies
        
        count, addresses = await proxy_manager.import_proxies(self.proxy_import_text)
        
        # Update stats
        all_proxies = get_best_proxies(limit=2000)
        self.proxy_stats_total = len(all_proxies)
        self.proxy_stats_elite = sum(1 for p in all_proxies if p.get('anonymity') == 'elite')
        
        self.proxy_import_text = ""
        self.is_importing_proxies = False
        self.add_log(f"Proxy import complete. Imported {count} proxies.")
        yield
