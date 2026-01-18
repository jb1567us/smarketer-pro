from .researcher import ResearcherAgent
import asyncio
from typing import List, Dict

class InfluencerAgent(ResearcherAgent):
    def __init__(self, provider=None):
        super().__init__(provider=provider)
        self.role = "Influencer Scout"
        self.goal = "Find high-impact creators and influencers in specific niches."

    async def scout_influencers(self, niche: str, platform: str = "instagram", limit: int = 10) -> List[Dict]:
        """
        Finds influencers by constructing specific search footprints.
        """
        # 1. Construct Footprint
        # e.g. site:instagram.com "fitness coach" "dm for collab"
        
        search_terms = [
            f'site:{platform}.com "{niche}" "follower"',
            f'site:{platform}.com "{niche}" "business inquiries"',
            f'site:{platform}.com "{niche}" "dm for collab"',
            f'site:{platform}.com "{niche}" "ambassador"'
        ]
        
        all_results = []
        
        # 2. Search (Simulated mass harvest across terms)
        for term in search_terms[:2]: # Limit to 2 queries for speed in MVP
            res = await self.mass_harvest(term, num_results=limit)
            all_results.extend(res)
            
        # 3. Deduplicate and Enrich
        unique_urls = list({r['url']: r for r in all_results}.values())
        
        # 4. Analyze/Estimate stats (Using LLM heuristic on snippet/title if real scraping is hard)
        analyzed_influencers = []
        
        for item in unique_urls:
            if len(analyzed_influencers) >= limit:
                break

            handle = self._extract_handle(item['url'], platform)
            
            # --- START QUALITY FILTER ---
            # 1. Check Domain Validity (Anti-Spoof/Junk TLDs)
            # 1. Check Domain Validity (Anti-Spoof/Junk TLDs)
            from urllib.parse import urlparse
            try:
                parsed = urlparse(item['url'])
                hostname = parsed.hostname.lower() if parsed.hostname else ""
                
                valid_domains = {
                    "instagram": "instagram.com",
                    "twitter": ["twitter.com", "x.com"],
                    "tiktok": "tiktok.com",
                    "youtube": "youtube.com",
                    "linkedin": "linkedin.com"
                }
                
                req = valid_domains.get(platform)
                if req:
                    # Convert single string to list for uniform handling
                    if isinstance(req, str): req = [req]
                    
                    # Check if hostname ends with any allowed domain (handling subdomains)
                    if not any(hostname.endswith(d) for d in req):
                        continue
                        
                # Strict Punycode Check on Hostname
                if "xn--" in hostname:
                    continue
            except:
                continue # Skip malformed URLs

            # 2. Check Bot/Junk Handle
            if self._is_likely_bot(handle):
                # print(f"Skipping probable bot/low-quality handle: {handle}")
                continue
            # --- END QUALITY FILTER ---

            # Basic parsing of title/snippet from search result
            title = item.get('title', '')
            snippet = item.get('snippet', '') # Now available thanks to Researcher fix
            
            profile_data = {
                "handle": handle,
                "url": item['url'],
                "platform": platform,
                "niche": niche,
                "estimated_followers": "Unknown", # Would need real scrape
                "bio_snippet": snippet or title
            }
            analyzed_influencers.append(profile_data)
            
        return analyzed_influencers

    def _is_likely_bot(self, handle: str) -> bool:
        """Heuristic to filter out junk handles."""
        if handle == "Unknown": return True
        
        import re
        # Check for excessive digits at end (e.g. user29384729)
        if re.search(r'\d{5,}$', handle):
            return True
            
        # Check for numeric-only or very short junk (handled by regex mostly)
        # Check for specific junk keywords in handle
        junk_kws = ['bot', 'crawler', 'scaper', 'test_account']
        if any(k in handle.lower() for k in junk_kws):
            return True
            
        return False

    def _extract_handle(self, url: str, platform: str) -> str:
        """Extracts @handle from URL."""
        try:
            if platform in url:
                parts = url.rstrip('/').split('/')
                return f"@{parts[-1]}"
        except:
            pass
        return "Unknown"

    async def analyze_profile(self, url: str):
        """
        Deep analysis of a specific profile (calls Parent enrich but focuses on creator metrics).
        """
        data = await self.enrich_lead_data(url)
        # Add custom logic here if needed
        return data
