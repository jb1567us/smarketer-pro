from .researcher import ResearcherAgent
import asyncio
import aiohttp
from typing import List, Dict

class InfluencerAgent(ResearcherAgent):
    def __init__(self, provider=None):
        super().__init__(provider=provider)
        self.role = "Influencer Scout"
        self.goal = "Find high-impact creators and influencers in specific niches."

    async def scout_influencers(self, niche: str, platform: str = "instagram", limit: int = 10, min_followers: int = 0, max_followers: int = 0) -> List[Dict]:
        """
        Finds influencers by constructing specific search footprints.
        Uses an iterative strategy: High Intent -> Broad -> Deep.
        """
        # Define Search Tiers and Common Negative Terms
        junk_terms = '-inurl:reel -inurl:p -inurl:stories -inurl:tags -inurl:explore -inurl:help -inurl:blog -inurl:newsroom -inurl:developer -inurl:ads -inurl:safety'
        
        search_tiers = []
        
        if platform == "instagram":
             # Tier 1: High Intent (Contact Info)
            search_tiers.append([
                f'site:{platform}.com "{niche}" "business inquiries" {junk_terms}',
                f'site:{platform}.com "{niche}" "email" {junk_terms}',
                f'site:{platform}.com "{niche}" "contact" {junk_terms}'
            ])
            # Tier 2: Growth/Stats
            search_tiers.append([
                f'site:{platform}.com "{niche}" "follower" {junk_terms}',
                f'site:{platform}.com "{niche}" "ambassador" {junk_terms}'
            ])
            # Tier 3: Broad Niche Match (High Volume, needing more filtering)
            search_tiers.append([
                f'site:{platform}.com "{niche}" {junk_terms}'
            ])
        else:
            # Generic fallback for other platforms
            search_tiers.append([
                f'site:{platform}.com "{niche}" "business inquiries" {junk_terms}',
                f'site:{platform}.com "{niche}" "email" {junk_terms}'
            ])
            search_tiers.append([
                f'site:{platform}.com "{niche}" "follower" {junk_terms}'
            ])
            # Threads.net specific support if requested
            if platform == "threads":
                 search_tiers.append([
                    f'site:threads.net "{niche}" {junk_terms}'
                ])
        
        analyzed_influencers = []
        seen_urls = set()
        
        from extractor import fetch_html
        import aiohttp # Ensure imported here if not at top level, though it is at file level
        
        # Iterative Search Loop
        async with aiohttp.ClientSession() as session:
            for tier_idx, tier_terms in enumerate(search_tiers):
                if len(analyzed_influencers) >= limit:
                    break
                
                print(f"  [InfluencerAgent] Entering Search Tier {tier_idx + 1} with {len(tier_terms)} terms...")
                
                # Dynamic relaxation: If we are deep in tiers (Tier 3) or have very few results, relax junk terms
                current_junk = junk_terms
                if tier_idx > 1 or (tier_idx > 0 and len(analyzed_influencers) == 0):
                    # Remove some strict negative keywords to strict discovery
                    current_junk = '-inurl:tags -inurl:explore -inurl:help -inurl:blog -inurl:newsroom'
                    print("  [InfluencerAgent] Relaxing negative constraints to improve yield.")
                
                for term in tier_terms:
                    # Apply current junk terms
                    # We assume 'term' has the original junk_terms placeholder or we reconstruct it
                    # But simpler: The term string ALREADY has the junk_terms in it. 
                    # We need to replace the original junk string with the new one if changed.
                    if current_junk != junk_terms:
                        term = term.replace(junk_terms, current_junk)

                    if len(analyzed_influencers) >= limit:
                        break
                        
                    # Harvest larger batch to filter down
                    raw_results = await self.mass_harvest(term, num_results=50) # Increased from default
                    
                    # Deduplicate immediately against session seen_urls
                    new_unique = []
                    for r in raw_results:
                        if r['url'] not in seen_urls:
                            seen_urls.add(r['url'])
                            new_unique.append(r)
                            
                    print(f"  [InfluencerAgent] Term '{term}' yielded {len(new_unique)} new unique URLs.")

                    # Analyze this batch
                    for item in new_unique:
                        if len(analyzed_influencers) >= limit:
                            break

                        handle = self._extract_handle(item['url'], platform)
                        
                        # --- START QUALITY FILTER ---
                        if handle == "Unknown" or handle is None:
                            continue

                        # 1. Check Domain Validity (Anti-Spoof/Junk TLDs)
                        from urllib.parse import urlparse
                        try:
                            parsed = urlparse(item['url'])
                            hostname = parsed.hostname.lower() if parsed.hostname else ""
                            
                            # Strict Punycode Check
                            if "xn--" in hostname:
                                continue
                                
                            # Strict Hostname Logic
                            # Must be exactly "platform.com" or "www.platform.com" or mobile "m.platform.com"
                            # Explicitly reject "ads.", "business.", "help.", "newsroom.", "developers."
                            
                            allowed_hosts = {
                                f"{platform}.com",
                                f"www.{platform}.com",
                                f"m.{platform}.com"
                            }
                            
                            if platform == "threads":
                                allowed_hosts.update(["threads.net", "www.threads.net"])
                            
                            if platform in ["twitter", "x"]:
                                allowed_hosts.update(["x.com", "www.x.com", "mobile.twitter.com"])
                                
                            if hostname not in allowed_hosts:
                                # print(f"Skipping non-canonical subdomain: {hostname}")
                                continue
                                
                            # Check Path against Junk Lists
                            path = parsed.path.lower()
                            junk_paths = [
                                "/reel/", "/p/", "/stories/", "/tags/", "/explore/", 
                                "/help", "/about", "/legal", "/safety", "/guidelines", 
                                "/developer", "/ads", "/newsroom"
                            ]
                            
                            if any(jp in path for jp in junk_paths):
                                continue

                        except:
                            continue 

                        # 2. Check Bot/Junk Handle
                        if self._is_likely_bot(handle):
                            continue
                        # --- END QUALITY FILTER ---

                        title = item.get('title', '')
                        snippet = item.get('snippet', '')

                        # --- FOLLOWER HARVESTING & BIO EXTRACTION ---
                        metrics = {"follower_count": "Unknown", "audience_sample": [], "bio": ""}
                        try:
                            html = await fetch_html(session, item['url'])
                            # Pass snippet/title as fallback context
                            metrics = self.get_profile_metrics(html, platform, item.get('snippet', ''), item.get('title', ''))
                            if html:
                                 metrics["audience_sample"] = self.harvest_audience_sample(html, platform)
                        except Exception as e:
                            print(f"Error harvesting metrics for {handle}: {e}")
                            # Fallback if fetch fails entirely
                            metrics = self.get_profile_metrics("", platform, item.get('snippet', ''), item.get('title', ''))

                        final_bio = metrics.get('bio')
                        if not final_bio:
                            if snippet and not snippet.startswith("http"):
                                 final_bio = snippet
                            elif title and not title.startswith("http"):
                                 final_bio = title
                            else:
                                 final_bio = "No bio available"

                        profile_data = {
                            "handle": handle,
                            "url": item['url'],
                            "platform": platform,
                            "niche": niche,
                            "estimated_followers": metrics.get("follower_count", "Unknown"),
                            "audience_sample": metrics.get("audience_sample", []),
                            "bio_snippet": final_bio
                        }
                        
                        # --- FOLLOWER FILTERING ---
                        if min_followers > 0 or max_followers > 0:
                            count_val = self._parse_follower_count(metrics.get("follower_count", "0"))
                            if min_followers > 0 and count_val < min_followers:
                                continue
                            if max_followers > 0 and count_val > max_followers:
                                continue
                            if count_val == 0 and min_followers > 0:
                                # Skip unknowns if we have a strict min requirement
                                continue
                                
                        analyzed_influencers.append(profile_data)
            
        self.save_work(analyzed_influencers, artifact_type="influencer_list", metadata={"niche": niche, "platform": platform})
        return analyzed_influencers

    def get_profile_metrics(self, html: str, platform: str, snippet_fallback: str = "", title_fallback: str = "") -> Dict:
        """
        Parses HTML to find follower counts and BIO.
        Uses snippet/title as fallback if HTML parsing fails or is empty.
        """
        metrics = {"follower_count": "Unknown", "bio": ""}
        import re
        
        # Combine all text sources for broader regex search if HTML fails
        all_text = (html or "") + " " + snippet_fallback + " " + title_fallback
        
        # --- STRATEGY 1: HTML Meta Tags (Most Accurate) ---
        if html:
            if platform == "instagram":
                # Look for meta description: e.g. "10M Followers, 200 Following, 500 Posts..."
                match = re.search(r'content="([^"]*?Followers[^"]*?)"', html, re.IGNORECASE)
                if match:
                    content = match.group(1)
                    parts = content.split(',')
                    for p in parts:
                        if "Followers" in p:
                             metrics["follower_count"] = p.strip().split(' ')[0]
                    
                    if " - " in content:
                        bio_part = content.split(" - ")[-1]
                        if "See Instagram photos" not in bio_part:
                            metrics["bio"] = bio_part.strip()
                
                if not metrics["bio"]:
                     # Try og:title: "Name (@handle) on Instagram: 'Bio...'"
                     title_match = re.search(r'<meta property="og:title" content="([^"]+)"', html)
                     if title_match:
                         t_content = title_match.group(1)
                         if ": " in t_content:
                             metrics["bio"] = t_content.split(": ")[-1].strip("'\"")

            elif platform in ["twitter", "x"]:
                 match = re.search(r'content="([^"]*?Followers[^"]*?)"', html, re.IGNORECASE)
                 if match:
                     content = match.group(1)
                     metrics["follower_count"] = content.split(' ')[0]
                     
                 if desc_match:
                     metrics["bio"] = desc_match.group(1)

            elif platform == "threads":
                # Try to find the hidden JSON blob in data-sjs script
                try:
                    import json
                    scripts = re.findall(r'<script type="application/json" data-sjs>(.*?)</script>', html, re.DOTALL)
                    for s_content in scripts:
                        # Simple Json Regex Fallback
                        f_match = re.search(r'"follower_count":\s*(\d+)', s_content)
                        if f_match:
                            metrics["follower_count"] = f_match.group(1)
                        
                        bio_match = re.search(r'"biography":\s*"([^"]+)"', s_content)
                        if bio_match:
                            metrics["bio"] = bio_match.group(1).encode('utf-8').decode('unicode_escape')
                except:
                    pass

        # --- STRATEGY 2: Fallback Regex on Snippet/Title (If Strategy 1 Failed) ---
        if metrics["follower_count"] == "Unknown":
            # Patterns like: "10K Followers", "1.5M Followers", "5,000 Followers"
            # Look in snippet and title specifically first
            start_sources = [snippet_fallback, title_fallback]
            for source in start_sources:
                if not source: continue
                fallback = re.search(r'([\d.,KM]+)\s+Followers', source, re.IGNORECASE)
                if fallback:
                    val = fallback.group(1)
                    # Basic validation: ensure it looks like a number
                    if any(c.isdigit() for c in val):
                        metrics["follower_count"] = val
                        break

        # Fallback Bio from Snippet if HTML bio failed
        if not metrics["bio"] and snippet_fallback:
             # Often snippet is: "X Followers, Y Following - Bio text..."
             if "Followers" in snippet_fallback and "-" in snippet_fallback:
                 potential_bio = snippet_fallback.split("-")[-1].strip()
                 if "See Instagram" not in potential_bio:
                     metrics["bio"] = potential_bio

        return metrics

    def harvest_audience_sample(self, html: str, platform: str) -> List[str]:
        """Attempts to find visible handles of potential followers/commenters."""
        if not html: return []
        audience = set()
        import re
        
        mentions = re.findall(r'@([a-zA-Z0-9_.]+)', html)
        junk = ['instagram', 'twitter', 'tiktok', 'youtube', 'home', 'login', 'support']
        
        for m in mentions:
            if len(m) > 3 and m.lower() not in junk:
                audience.add(f"@{m}")
                
        return list(audience)[:5]

    def _parse_follower_count(self, count_str: str) -> int:
        """
        Parses strings like '10K', '1.5M', '500', '10,000' into integers.
        Returns 0 if parsing fails or input is None/Unknown.
        """
        if not count_str or count_str == "Unknown":
            return 0
            
        s = count_str.upper().replace(",", "").strip()
        
        try:
            if "K" in s:
                # 10.5K -> 10500
                num = float(s.replace("K", ""))
                return int(num * 1000)
            elif "M" in s:
                # 1.5M -> 1500000
                num = float(s.replace("M", ""))
                return int(num * 1_000_000)
            elif "B" in s:
                num = float(s.replace("B", ""))
                return int(num * 1_000_000_000)
            else:
                return int(float(s))
        except:
            return 0

    def _is_likely_bot(self, handle: str) -> bool:
        """Heuristic to filter out junk handles."""
        if handle == "Unknown": return True
        
        import re
        if re.search(r'\d{5,}$', handle):
            return True
            
        junk_kws = ['bot', 'crawler', 'scaper', 'test_account']
        if any(k in handle.lower() for k in junk_kws):
            return True
            
        return False

    def _extract_handle(self, url: str, platform: str) -> str:
        """Extracts @handle from URL."""
        try:
            # Handle generic platform match or specific host
            if platform in url or (platform == "threads" and "threads.net" in url):
                # Filter out reel/post URLs if they slip through
                # Check for /reel/, /reels/, /p/, /explore/, /tags/
                if any(x in url for x in ["/reel/", "/reels/", "/p/", "/explore/", "/tags/", "/stories/"]):
                    return "Unknown"
                
                parts = url.rstrip('/').split('/')
                potential_handle = parts[-1]
                
                if "?" in potential_handle:
                    potential_handle = potential_handle.split('?')[0]
                    
                # Enhanced Blocklist
                if potential_handle.lower() in ["reel", "reels", "p", "explore", "stories", "tags", "live", "tv", "shop", "creator", "about"]:
                    return "Unknown"
                    
                return f"@{potential_handle}"
        except:
            pass
        return "Unknown"

    async def analyze_profile(self, url: str):
        """
        Deep analysis of a specific profile (calls Parent enrich but focuses on creator metrics).
        """
        data = await self.enrich_lead_data(url)
        return data
