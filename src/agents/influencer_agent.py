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
        Finds influencers using advanced platform-specific Dorks and signal detection.
        Supports: Instagram, TikTok, YouTube, Twitter, LinkedIn.
        """
        # Parse limits
        min_f = self._parse_follower_count(min_followers) if min_followers else 0
        max_f = self._parse_follower_count(max_followers) if max_followers else float('inf')
        
        platform = platform.lower()
        search_terms = []
        
        # --- Platform Specific Dork Strategies (Derived from 'dorks/' folder) ---
        
        if platform == "instagram":
            # Core noise filter: exclude tags, posts, reels, explore
            # Core noise filter: [MODIFIED] Removed negative operators per user request
            # [UPDATE] Re-added -inurl:reels as requested
            base = 'site:instagram.com -inurl:reels'
            
            # 1. Profile Search (Broadened - restrictive modifiers removed per user request)
            if city:
                search_terms.append(f'{base} "{niche}" "{city}"')
            else:
                search_terms.append(f'{base} "{niche}"')
                
            # [SAVED] Previous Restrictive Dorks (1-4)
            # 1. Profile w/ Keywords: search_terms.append(f'{base} "{niche}" ("content creator" OR influencer OR creator OR "ugc")')
            # 2. Collab Signals:      search_terms.append(f'{base} "{niche}" ("DM for collabs" OR collabs OR "brand ambassador" OR PR OR gifted)')
            # 3. Business Signals:    search_terms.append(f'{base} "{niche}" ("email" OR booking OR inquiries OR "media kit" OR "rate card" OR "gmail.com")')
            # 4. Deal-Ready:          search_terms.append(f'{base} "{niche}" ("amazon storefront" OR "LTK" OR "shop my" OR "discount code")')

            # 5. Link-in-Bio Targeting (Kept active)
            bio_domains = '("linktr.ee" OR "beacons.ai" OR "campsite.bio" OR "taplink" OR "bio.site" OR "lnk.bio" OR "hopp.co" OR "carrd.co" OR "stan.store")'
            search_terms.append(f'{base} "{niche}" {bio_domains}')

        elif platform == "tiktok":
            # Core noise filter: profiles only (inurl:/@) AND exclude video pages, tags, music
            base = 'site:tiktok.com inurl:/@ -inurl:/video/ -inurl:/tag/ -inurl:/music/ -inurl:/discover -inurl:/search'
            
            # 1. Profile Search
            if city:
                search_terms.append(f'{base} "{niche}" "{city}" (creator OR influencer OR "content creator")')
            else:
                search_terms.append(f'{base} "{niche}" (creator OR influencer OR "content creator")')
            
            # 2. Collab Signals
            search_terms.append(f'{base} "{niche}" ("collab" OR "brand deals" OR "paid partnership" OR "work with" OR "PR package")')
            
            # 3. Contact Info
            search_terms.append(f'{base} "{niche}" ("email" OR booking OR inquiries OR "media kit" OR "gmail.com")')
            
            # 4. Deal Ready
            search_terms.append(f'{base} "{niche}" ("ugc" OR sponsored OR affiliate OR "discount code" OR "amazon storefront")')

        elif platform == "youtube":
            # Core noise filter: channels only (/@, /c/, /channel/, /user/) AND exclude watch/shorts
            base = 'site:youtube.com (inurl:/@ OR inurl:/c/ OR inurl:/channel/ OR inurl:/user/) -inurl:/watch -inurl:/shorts -inurl:/results'
            
            # 1. Channel Search
            search_terms.append(f'{base} "{niche}" ("creator" OR "content creator" OR influencer)')
            
            # 2. Sponsorship/Contact
            search_terms.append(f'{base} "{niche}" ("business inquiries" OR sponsorship OR "brand deals" OR "email" OR "media kit")')
            
            # 3. About Page Email (Simulated by targeting text that appears on About tab)
            search_terms.append(f'{base} "{niche}" "view email address"')
            
            # 4. Deal Ready
            search_terms.append(f'{base} "{niche}" (sponsored OR affiliate OR "discount code" OR ambassador)')

        elif platform == "linkedin":
            # Core noise filter: profiles (inurl:in) AND exclude jobs, learning, posts
            base = 'site:linkedin.com/in -inurl:jobs -inurl:learning -inurl:pulse -inurl:feed -inurl:posts'
            
            # 1. Profile Search
            search_terms.append(f'{base} "{niche}" (creator OR "content creator" OR influencer OR speaker OR consultant)')
            
            # 2. Creator Signals
            search_terms.append(f'{base} "{niche}" ("newsletter" OR "creator" OR "thought leader" OR "public speaker")')
            
            # 3. Partnerships
            search_terms.append(f'{base} "{niche}" (partnerships OR sponsorship OR "brand" OR "work with" OR booking OR "media kit")')
            
            # 4. Explicit "Open To"
            search_terms.append(f'{base} "{niche}" ("open to partnerships" OR "brand partnerships")')

        elif platform == "twitter" or platform == "x":
            # Core noise filter: exclude status, hashtags
            base_x = 'site:x.com -inurl:/status/ -inurl:/i/ -inurl:/hashtag -inurl:/search'
            base_tw = 'site:twitter.com -inurl:/status/ -inurl:/i/ -inurl:/hashtag -inurl:/search'
            
            # For X, we iterate primarily on x.com, but can fallback. 
            # Sticking to x.com for cleaner results as it's the specific request often.
            
            # 1. Profile Search
            search_terms.append(f'{base_x} "{niche}" (creator OR influencer OR newsletter OR podcast)')
            
            # 2. Collab Signals
            search_terms.append(f'{base_x} "{niche}" ("DM for collabs" OR collabs OR sponsorship OR "brand deals")')
            
            # 3. Contact
            search_terms.append(f'{base_x} "{niche}" (email OR booking OR inquiries OR "media kit")')

        else:
            # Generic Fallback
            search_terms.append(f'site:{platform}.com "{niche}"')

        # --- Reverse Search Strategies (All Platforms) ---
        # Searching the bio link providers directly for the niche + platform
        bridge_providers = [
            "site:linktr.ee", "site:beacons.ai", "site:campsite.bio", 
            "site:taplink.cc", "site:bio.site", "site:lnk.bio", 
            "site:direct.me", "site:stan.store", "site:carrd.co",
            "site:mainstack.me", "site:hoo.be", "site:snipfeed.co", "site:solo.to"
        ]
        
        # Add reverse searches (limit to a few to avoid spamming if many dorks already)
        if len(search_terms) < 6:
            for provider in bridge_providers:
                # E.g. site:linktr.ee "fitness" instagram
                search_terms.append(f'{provider} "{niche}" {platform}')
                if len(search_terms) >= 12: break

        
        print(f"DEBUG: Generated {len(search_terms)} Superior Dorks for {platform} in {niche}")
        
        # --- Execution (Unified Global Harvester) ---
        from src.global_search_harvester import GlobalSearchHarvester
        
        print(f"🚀 [InfluencerAgent] Launching Global Harvester for {len(search_terms)} dork strategies...")
        
        harvest_tasks = []
        for term in search_terms:
            # Adaptive result count
            count = 20 if len(search_terms) < 5 else 10
            
            harvest_tasks.append({
                'query': term, 
                'platform': 'google', 
                'num_results': count,
                'dork': term,
                'keyword': niche
            })
            
        # Run Concurrent Harvester
        # We use 4 workers to speed up the process significantly compared to sequential
        harvester = GlobalSearchHarvester(input_data=harvest_tasks, workers=4)
        raw_results = await harvester.run()
        
        all_results = []
        for r in raw_results:
             all_results.append({
                 "url": r.get('url'),
                 "source_type": "profile",
                 "title": r.get('title'),
                 "snippet": r.get('snippet', '')
             })
        
        # --- Filtering & Analysis ---
        unique_urls = list({r['url']: r for r in all_results}.values())
        analyzed_influencers = []
        
        allowed_domains_map = {
            "instagram": ["instagram.com"],
            "tiktok": ["tiktok.com"],
            "youtube": ["youtube.com"],
            "linkedin": ["linkedin.com"],
            "twitter": ["twitter.com", "x.com"],
            "x": ["twitter.com", "x.com"]
        }
        
        # Bridge domains are valid initial hits, we will resolve them or keep them
        bridge_roots = [
            "linktr.ee", "beacons.ai", "campsite.bio", "taplink.cc", "taplink.at",
            "bio.site", "lnk.bio", "direct.me", "stan.store", "carrd.co",
            "mainstack.me", "hoo.be", "snipfeed.co", "solo.to"
        ]
        
        target_roots = allowed_domains_map.get(platform, []) + bridge_roots
        
        for item in unique_urls:
            if len(analyzed_influencers) >= limit: break
            
            url = item['url']
            from urllib.parse import urlparse
            try:
                domain = urlparse(url).hostname.lower()
                if not any(root in domain for root in target_roots):
                    continue
            except:
                continue
                
            handle = self._extract_handle(url, platform)
            if self._is_likely_bot(handle): continue
            
            # --- Validated Stats ---
            follower_count_str = "Unknown"
            validated_count = 0
            
            if min_f > 0 or max_f < float('inf'):
                # Deep Scrape
                try:
                    scrape_data = await self.scraper.smart_scrape(url, platform=platform)
                    if scrape_data:
                        stats = scrape_data.get('extracted_stats', {}) or {}
                        raw_count = stats.get('followers', "0")
                        validated_count = self._parse_follower_count(str(raw_count))
                        follower_count_str = str(raw_count)
                        
                        if validated_count < min_f: continue
                        if validated_count > max_f: continue
                except Exception as e:
                    print(f"Stats validation failed for {url}: {e}")
                    continue
            else:
                 # Check snippet for "X Followers" signal if available
                 import re
                 snippet = item.get('snippet', '')
                 # Regex for "10K followers" or "5.5M Followers"
                 match = re.search(r'([\d\.,]+[KMB]?)\s+Followers', snippet, re.IGNORECASE)
                 if match:
                     follower_count_str = match.group(1)

            profile_data = {
                "handle": handle,
                "url": url,
                "platform": platform,
                "niche": niche,
                "estimated_followers": follower_count_str,
                "bio_snippet": item.get('snippet', '') or item.get('title', '')
            }
            analyzed_influencers.append(profile_data)

        # Auto-save
        try:
            from src.database import bulk_save_influencers
            bulk_save_influencers(analyzed_influencers)
        except: pass
        
        return analyzed_influencers

    async def mass_harvest(self, footprint, num_results=100, status_callback=None):
        """
        Influencer-specific harvester: Forces high-fidelity engines (Google/Bing)
        to respect complex Dorks strategies.
        """
        if status_callback: status_callback(f"🚀 Starting Mass Harvest for: '{footprint}'")
        print(f"DEBUG: InfluencerAgent mass_harvest called with footprint: {footprint}")
        
        # Imports needed since we removed the previous block
        from scraper import search_searxng
        import aiohttp

        async with aiohttp.ClientSession() as session:
            # [MODIFIED] Using DirectBrowser integration
            raw_results = await search_searxng(
                footprint, 
                session, 
                num_results=num_results
                # engines=engines  <-- Ignored by DirectBrowser
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
