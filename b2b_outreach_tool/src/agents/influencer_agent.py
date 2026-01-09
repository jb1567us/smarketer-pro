from .researcher import ResearcherAgent
import asyncio
import aiohttp
from typing import List, Dict

class InfluencerAgent(ResearcherAgent):
    def __init__(self, provider=None):
        super().__init__(provider=provider)
        self.role = "Influencer Scout"
        self.goal = "Find high-impact creators and influencers in specific niches."

    async def scout_influencers(self, niche: str, platform: str = "instagram", limit: int = 10) -> List[Dict]:
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
                            if html:
                                 metrics = self.get_profile_metrics(html, platform)
                                 metrics["audience_sample"] = self.harvest_audience_sample(html, platform)
                        except Exception as e:
                            print(f"Error harvesting metrics for {handle}: {e}")

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
                        analyzed_influencers.append(profile_data)
            
        self.save_work(analyzed_influencers, artifact_type="influencer_list", metadata={"niche": niche, "platform": platform})
        return analyzed_influencers

    def get_profile_metrics(self, html: str, platform: str) -> Dict:
        """Parses HTML to find follower counts and BIO."""
        metrics = {"follower_count": "Unknown", "bio": ""}
        
        # Regex heuristics for common platforms
        # Note: These are fragile and depend on platform DOM stability
        import re
        
        if platform == "instagram":
            # Look for meta description: e.g. "10M Followers, 200 Following, 500 Posts - See Instagram photos and videos from @user"
            # It usually contains the bio after the stats sometimes, or we can check og:title
            match = re.search(r'content="([^"]*?Followers[^"]*?)"', html, re.IGNORECASE)
            if match:
                content = match.group(1)
                # content looks like "X Followers, Y Following, Z Posts - ... "
                
                # Extract Stats
                parts = content.split(',')
                for p in parts:
                    if "Followers" in p:
                         metrics["follower_count"] = p.strip().split(' ')[0]
                
                # Extract Bio / Description part (usually after ' - ')
                if " - " in content:
                    bio_part = content.split(" - ")[-1]
                    # Filter out generic "See Instagram photos..."
                    if "See Instagram photos" not in bio_part:
                        metrics["bio"] = bio_part.strip()
            
            if not metrics["bio"]:
                 # Try og:title
                 title_match = re.search(r'<meta property="og:title" content="([^"]+)"', html)
                 if title_match:
                     t_content = title_match.group(1)
                     # usually "Name (@handle) on Instagram: 'Bio...'"
                     if ": " in t_content:
                         metrics["bio"] = t_content.split(": ")[-1].strip("'\"")

        elif platform in ["twitter", "x"]:
             # Often obscured in JS, but sometimes in meta
             # "X Followers"
             match = re.search(r'content="([^"]*?Followers[^"]*?)"', html, re.IGNORECASE)
             if match:
                 content = match.group(1)
                 metrics["follower_count"] = content.split(' ')[0] # Very rough
                 
             # Twitter Description
             desc_match = re.search(r'<meta property="og:description" content="([^"]+)"', html)
             if desc_match:
                 metrics["bio"] = desc_match.group(1)

        elif platform == "tiktok":
             # <strong title="Followers">100K</strong>
             # Hard without rendering
             pass
             
        # Fallback: Look for generic "X Followers" patterns in text
        if metrics["follower_count"] == "Unknown":
            # Simple fallback regex for "10K Followers"
            # 10K, 10.5M, 1,200
            fallback = re.search(r'([\d.,KM]+)\s+Followers', html, re.IGNORECASE)
            if fallback:
                 metrics["follower_count"] = fallback.group(1)

        return metrics

    def harvest_audience_sample(self, html: str, platform: str) -> List[str]:
        """Attempts to find visible handles of potential followers/commenters."""
        audience = set()
        import re
        
        # Look for @mentions in text
        # (This captures anyone mentioned, likely other users/followers)
        mentions = re.findall(r'@([a-zA-Z0-9_.]+)', html)
        
        # Filter common junk
        junk = ['instagram', 'twitter', 'tiktok', 'youtube', 'home', 'login', 'support']
        
        for m in mentions:
            if len(m) > 3 and m.lower() not in junk:
                audience.add(f"@{m}")
                
        return list(audience)[:5] # Return top 5 sample

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
                # Filter out reel/post URLs if they slip through
                if "/reel/" in url or "/p/" in url:
                    # Try to see if it's like instagram.com/user/reel/ID (rare)
                    # Usually it's instagram.com/reel/ID which has NO user info
                    return "Unknown"
                
                # Basic clean path extraction
                # e.g. https://www.instagram.com/michelle_lewin/ -> michelle_lewin
                parts = url.rstrip('/').split('/')
                potential_handle = parts[-1]
                
                # Ignore query params
                if "?" in potential_handle:
                    potential_handle = potential_handle.split('?')[0]
                    
                if potential_handle in ["reel", "p", "explore", "stories"]:
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
        # Add custom logic here if needed
        return data
