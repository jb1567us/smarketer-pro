from .researcher import ResearcherAgent
import asyncio
from typing import List, Dict
import pandas as pd
from src.social_scraper import SocialScraper, parse_social_stats

class InfluencerAgent(ResearcherAgent):
    def __init__(self, provider=None):
        super().__init__(provider=provider)
        self.role = "Influencer Scout"
        self.goal = "Find high-impact creators and influencers in specific niches."
        self.scraper = SocialScraper()

    def _parse_follower_count(self, count_str):
        """Converts strings like '10K', '1.5M' to integers."""
        if not count_str: return 0
        s = str(count_str).upper().replace(',', '').replace('FOLLOWERS', '').replace('SUBSCRIBERS', '').strip()
        multiplier = 1
        if 'K' in s:
            multiplier = 1000
            s = s.replace('K', '')
        elif 'M' in s:
            multiplier = 1000000
            s = s.replace('M', '')
        elif 'B' in s:
            multiplier = 1000000000
            s = s.replace('B', '')
        
        try:
            return int(float(s) * multiplier)
        except:
            return 0

    async def scout_influencers(self, niche: str, platform: str = "instagram", limit: int = 10, city: str = "", audience: str = "", min_followers=None, max_followers=None) -> List[Dict]:
        """
        Finds influencers by constructing specific search footprints.
        
        Args:
            niche: The main niche (e.g. "fitness", "skincare")
            platform: Platform to search (default: instagram)
            limit: Max results to return
            city: Optional city for geo-targeting (e.g. "Austin", "London")
            audience: Optional target audience (e.g. "new moms", "students")
            min_followers: Optional min count
            max_followers: Optional max count
        """
        # Parse limits if provided
        min_f = self._parse_follower_count(min_followers) if min_followers else 0
        max_f = self._parse_follower_count(max_followers) if max_followers else float('inf')

        # Ensure platform is instagram for now as requested by user or passed arg
        if platform.lower() != "instagram":
             # Fallback to simple site: logic for other platforms
             site_operator = f"site:{platform}.com"
             search_terms = [f'{site_operator} "{niche}"']
        else:
            # --- Advanced Instagram Dorks (Full Suite) ---
            # Restored per user request to include the full footprint list.
            base_filter = 'site:instagram.com -inurl:explore -inurl:tag -inurl:p -inurl:reel'
            link_bio_domains = '("linktr.ee" OR "beacons.ai" OR "campsite.bio" OR "taplink.cc" OR "taplink.at" OR "bio.site" OR "lnk.bio" OR "direct.me" OR "flow.page" OR "stan.store" OR "solo.to" OR "carrd.co")'
            
            search_terms = []
            
            # --- PRIORITY 1: Deal-Ready Signals (High Intent) ---
            # A. Paid/UGC/Ambassador [WAS Group 5]
            search_terms.append(f'{base_filter} "{niche}" ("ugc" OR "paid partnership" OR sponsored OR "brand deal" OR affiliate OR ambassador)')
            
            # B. Storefront/Affiliate
            search_terms.append(f'{base_filter} "{niche}" ("amazon storefront" OR "LTK" OR "shop my" OR "discount code")')
            
            # C. Contact Info/Business
            search_terms.append(f'{base_filter} "{niche}" ("email" OR booking OR inquiries OR "media kit" OR "rate card")')
            
            # --- PRIORITY 2: Link-in-Bio Specific ---
            # A. Standard
            search_terms.append(f'{base_filter} "{niche}" {link_bio_domains}')
            
            # B. With City
            if city:
                 search_terms.append(f'{base_filter} "{niche}" "{city}" {link_bio_domains}')
            
            # --- PRIORITY 3: Reverse-Search (Bridge Domains) ---
            reverse_providers = [
                "site:linktr.ee", "site:beacons.ai", "site:campsite.bio", 
                "site:taplink.cc", "site:taplink.at", "site:bio.site", 
                "site:lnk.bio", "site:direct.me", "site:flow.page", 
                "site:stan.store", "site:solo.to", "site:carrd.co"
            ]
            for provider in reverse_providers:
                query = f'{provider} "{niche}" instagram'
                if city:
                    query += f' "{city}"'
                search_terms.append(query)
                

        
        all_results = []
        
        # 2. Search (Simulated mass harvest across terms)
        import random
        per_category_limit = max(3, int(limit / max(1, len(search_terms) / 2))) # rough heuristic
        
        print(f"DEBUG: InfluencerAgent generated {len(search_terms)} dorks: {search_terms}")
        
        for term in search_terms: 
            res = await self.mass_harvest(term, num_results=per_category_limit)
            all_results.extend(res)
            
            if len(all_results) >= limit * 4: # Harvest 4x limit (was 2x) to ensure variety before filtering
                break
            
        # 3. Deduplicate and Enrich
        unique_urls = list({r['url']: r for r in all_results}.values())
        
        # 4. Analyze/Estimate stats
        analyzed_influencers = []
        
        # [STRICT FILTER] Define allowed domains based on platform
        allowed_domains_map = {
            "instagram": ["instagram.com"],
            "twitter": ["twitter.com", "x.com"],
            "tiktok": ["tiktok.com"],
            "youtube": ["youtube.com"],
            "linkedin": ["linkedin.com"]
        }
        allowed_roots = allowed_domains_map.get(platform, [])
        
        # [UPDATE] Allow Reverse Search "Bridge" Domains as valid results
        # These are commonly accepted as influencer profiles in this context
        bridge_roots = [
            "linktr.ee", "beacons.ai", "campsite.bio", "taplink.cc", "taplink.at", 
            "bio.site", "lnk.bio", "direct.me", "flow.page", "stan.store", "solo.to", "carrd.co"
        ]
        allowed_roots.extend(bridge_roots)
        
        for item in unique_urls:
            if len(analyzed_influencers) >= limit:
                break
                
            # STRICT DOMAIN CHECK
            from urllib.parse import urlparse
            try:
                parsed = urlparse(item['url'])
                hostname = parsed.hostname.lower() if parsed.hostname else ""
                
                # Must match one of the allowed roots
                if not any(root in hostname for root in allowed_roots):
                    # print(f"DEBUG: Dropping non-platform URL: {item['url']}")
                    continue
            except:
                continue

            handle = self._extract_handle(item['url'], platform)
            
            # --- START QUALITY FILTER ---
            # 1. Check Domain Validity (Anti-Spoof/Junk TLDs) - Redundant but kept for structure
            # (Already handled by strict check above)
            
            # 2. Check Bot/Junk Handle
            if self._is_likely_bot(handle):
                continue
            # --- END QUALITY FILTER ---

            # 2. Check Bot/Junk Handle
            if self._is_likely_bot(handle):
                # print(f"Skipping probable bot/low-quality handle: {handle}")
                continue
            # --- END QUALITY FILTER ---

            # --- FOLLOWER COUNT VALIDATION ---
            follower_count_str = "Unknown"
            validated_count = 0
            
            if min_f > 0 or max_f < float('inf'):
                # We MUST validate the profile to get stats
                print(f"  [Influencer Scout] Validating stats for {handle}...")
                scrape_data = await self.scraper.smart_scrape(item['url'], platform=platform)
                
                # Check for captured follower count
                raw_count = "0"
                if scrape_data:
                     # 1. Primary: Standardized parsed stats (X-Ray or lightweight)
                     if 'extracted_stats' in scrape_data and scrape_data['extracted_stats']:
                          raw_count = scrape_data['extracted_stats'].get('followers', "0")
                     
                     # 2. Secondary: Captured hidden data (Browser specific)
                     elif 'captured_hidden_data' in scrape_data:
                          raw_count = scrape_data['captured_hidden_data'].get('follower_count_raw', "0")
                          
                     # 3. Tertiary: Generic stats string
                     elif 'stats' in scrape_data and isinstance(scrape_data['stats'], str):
                          # Try to parse it on the fly if it hasn't been parsed
                          parsed = parse_social_stats(scrape_data['stats'])
                          if parsed: raw_count = parsed.get('followers', "0")

                validated_count = self._parse_follower_count(str(raw_count))
                follower_count_str = str(raw_count)
                
                # Apply Filters
                if validated_count < min_f:
                    print(f"    -> Dropped: Too small ({validated_count} < {min_f})")
                    continue
                if validated_count > max_f:
                    print(f"    -> Dropped: Too big ({validated_count} > {max_f})")
                    continue
                
                print(f"    -> MATCH: {validated_count} followers")
            # ---------------------------------

            # Basic parsing of title/snippet from search result
            title = item.get('title', '')
            snippet = item.get('snippet', '') # Now available thanks to Researcher fix
            
            profile_data = {
                "handle": handle,
                "url": item['url'],
                "platform": platform,
                "niche": niche,
                "estimated_followers": follower_count_str, 
                "bio_snippet": snippet or title
            }
            analyzed_influencers.append(profile_data)
            
        # [AUTO-SAVE] Save to Database
        try:
            from src.database import bulk_save_influencers
            saved_count = bulk_save_influencers(analyzed_influencers)
            print(f"  [Influencer Scout] Auto-saved {saved_count} candidates to database.")
        except Exception as e:
            print(f"  [Influencer Scout] Auto-save failed: {e}")

        return analyzed_influencers

    async def mass_harvest(self, footprint, num_results=100, status_callback=None):
        """
        Influencer-specific harvester: Forces high-fidelity engines (Google/Bing)
        to respect complex Dorks strategies.
        """
        if status_callback: status_callback(f"🚀 Starting Mass Harvest for: '{footprint}'")
        print(f"DEBUG: InfluencerAgent mass_harvest called with footprint: {footprint}")
        
        # Override engines to ensures dorks are respected
        # [FIX] Re-enabling Google/Bing as we now have high-quality proxies (Strict Mode)
        # Yahoo/Brave/Startpage/Qwant are persistently blocking (400/503).
        engines = ['google', 'bing', 'duckduckgo'] 
        
        # We must reimplement the search call logic here.
        from scraper import search_searxng
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            # We assume searching via global router/scraper
            raw_results = await search_searxng(
                footprint, 
                session, 
                num_results=num_results,
                engines=engines 
            )
            
            final_urls = []
            for res in raw_results:
                url = res['url']
                title = res['title']
                
                # We skip list-parser logic for influencers as we want profiles, not lists of tools
                final_urls.append({"url": url, "source_type": "profile", "title": title, "snippet": res.get("snippet", "")})
            
            unique = {item['url']: item for item in final_urls}.values()
            return list(unique)[:num_results]

    async def think_async(self, context, instructions=None):
        """
        Interprets the task to see if it's an influencer scout mission.
        """
        # Combine context and instructions for intent detection
        intent_source = (str(context) + " " + str(instructions)).lower()
        
        # Check for keywords indicating an influencer search
        # We also check if we are just passed a niche (simple string) and instructions imply scouting
        # FORCE SCOUT MODE if we are the dedicated Influencer Agent
        # We don't want to fall back to generic research unless explicitly requested? 
        # Actually, let's just make the condition broader.
        is_scout_intent = (
            ("find" in intent_source and ("influencer" in intent_source or "creator" in intent_source)) 
            or (instructions and "find" in str(instructions).lower())
            or self.role == "Influencer Scout" # Always scout if this is the active agent!
        )

        if is_scout_intent:
            # Extract basic params (naive extraction for MVP)
            # Assuming context might be "Find 50 influencers in the [Niche] using hashtags"
            
            # Fallback niche if not obvious
            niche = "general"
                
            # Try to extract niche from string if possible, or use a default
            # For now, we'll assume the prompt engine or caller passes a structured request if possible.
            # If it's a raw string, we might just pass the whole string as the 'niche' equivalent 
            # or rely on the agent's internal logic. 
            # Let's use the 'task' or 'input_variable' from workflow if available (passed as dict)
            
            if isinstance(context, dict):
                niche = context.get("input_variable", context.get("niche", "fitness")) # fallback
                platform = context.get("platform", "instagram").lower()
                city = context.get("city", "")
                audience = context.get("audience", "")
                limit = int(context.get("limit", 10))
                min_followers = context.get("min_followers", None)
                max_followers = context.get("max_followers", None)
            else:
                # Text input - Use LLM to extract structured data for precise dorking
                # This ensures "Find fitness influencers in Austin" becomes niche="fitness", city="Austin"
                # instead of niche="find fitness influencers in austin"
                try:
                    extraction_prompt = (
                        f"Extract search parameters from this request: '{context}'\n"
                        "Look for 'Target Limit: X' (default 10), 'Min Followers: X', 'Max Followers: X'.\n"
                        "Return JSON strictly: {\"niche\": \"topic\", \"city\": \"city\", \"audience\": \"text\", \"platform\": \"instagram\", \"limit\": int, \"min_followers\": \"str_or_null\", \"max_followers\": \"str_or_null\"}"
                    )
                    extracted = self.provider.generate_json(extraction_prompt)
                    if isinstance(extracted, list): extracted = extracted[0]
                    
                    niche = extracted.get("niche")
                    if not niche or str(niche).lower() == "none":
                        niche = context

                    platform = extracted.get("platform", "instagram")
                    city = extracted.get("city", "")
                    audience = extracted.get("audience", "")
                    limit = int(extracted.get("limit", 10))
                    min_followers = extracted.get("min_followers", None)
                    max_followers = extracted.get("max_followers", None)
                except Exception as e:
                    print(f"DEBUG: Extraction failed, using raw input. Error: {e}")
                    niche = context
                    platform = "instagram"
                    city = ""
                    audience = ""
                    limit = 10
                    min_followers = None
                    max_followers = None
                
            return await self.scout_influencers(niche, platform=platform, city=city, audience=audience, limit=limit, min_followers=min_followers, max_followers=max_followers)
            
        # Default to standard researcher behavior if not specific to scouting
        return await super().think_async(context, instructions)

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
