from .base import BaseAgent
import json

class SEOExpertAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            role="SEO Expert & Growth Hacker",
            goal="Analyze websites for SEO optimizations, perform keyword research, and suggest backlink strategies to dominate search rankings.",
            provider=provider
        )

    def run(self, context):
        """
        Runs the SEO analysis.
        context can be a URL, a keyword, or a business description.
        """
        prompt = f"""
        Execute an SEO strategy or analysis based on the following context:
        {context}

        Provide a detailed report in JSON format with the following structure:
        {{
            "site_audit": {{
                "score": 0,
                "top_issues": [],
                "quick_fixes": []
            }},
            "keyword_research": {{
                "suggested_keywords": [
                    {{ "keyword": "", "difficulty": "Low/Med/High", "volume_est": "" }}
                ],
                "competition_analysis": ""
            }},
            "backlink_strategy": {{
                "opportunities": [],
                "competitor_backlinks": ""
            }},
            "content_ideas": []
        }}
        """
        return self.provider.generate_json(prompt)

    async def audit_site(self, url):
        import aiohttp
        from bs4 import BeautifulSoup
        from extractor import fetch_html
        
        async with aiohttp.ClientSession() as session:
            # Fetch real content
            html = await fetch_html(session, url)
            
            if not html:
                return {
                    "site_audit": {
                        "score": 0,
                        "top_issues": ["Could not access website"],
                        "quick_fixes": ["Check if the URL is correct", "Ensure site is online and not blocking bots"]
                    },
                    "note": "We attempted to scrape the site but got no content."
                }
            
            # Python-based Metrics Extraction
            soup = BeautifulSoup(html, 'html.parser')
            
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else "Missing"
            title_len = len(title)
            
            meta_desc_tag = soup.find('meta', attrs={"name": "description"})
            meta_desc = meta_desc_tag['content'].strip() if meta_desc_tag else "Missing"
            meta_len = len(meta_desc)
            
            h1_tags = soup.find_all('h1')
            h1_count = len(h1_tags)
            h1_content = [h.get_text().strip() for h in h1_tags][:3] # Top 3
            
            images = soup.find_all('img')
            img_count = len(images)
            missing_alt = sum(1 for img in images if not img.get('alt'))
            
            metrics = {
                "title": title,
                "title_length": title_len,
                "meta_description_length": meta_len,
                "h1_count": h1_count,
                "h1_content": h1_content,
                "total_images": img_count,
                "images_missing_alt": missing_alt
            }
            
            # Truncate for token limits
            context_content = html[:15000]
            
            prompt = f"""
            Perform a technical SEO audit based on the following REAL data:
            
            HARD METRICS (Derived from Code):
            {json.dumps(metrics, indent=2)}
            
            PAGE CONTENT PREVIEW (First 15k chars):
            {context_content}
            
            INSTRUCTIONS:
            1. Use the HARD METRICS to provide factual, non-hallucinated advice (e.g., "Title is {title_len} chars" rather than "Title seems short").
            2. If H1 count is 0, flag it as critical. If > 1, warn about focus.
            3. Check Meta Description length (ideal: 150-160).
            4. Analyze the text content for keyword usage.
            """
            
            result = self.run(prompt)
            
            # Robustness: Handle if LLM returns a list [ { ... } ]
            if isinstance(result, list) and len(result) > 0 and isinstance(result[0], dict):
                result = result[0]
            
            # Inject Hard Metrics into the result for display
            if isinstance(result, dict):
                result['metrics'] = metrics
                
            return result

    def research_keywords(self, niche):
        return self.run(f"Identify high-value, low-competition keywords for the niche: {niche}")

    def monitor_backlinks(self, domain):
        return self.run(f"Identify potential backlink opportunities and analyze the backlink profile for: {domain}")

    def design_link_wheel(self, money_site_url, niche, strategy="standard"):
        """
        Designs a multi-tier link wheel structure for authority funneling.
        strategy: 'standard', 'double', 'funnel'
        """
        prompt = f"""
        Design a highly effective SEO Link Wheel strategy for:
        Money Site: {money_site_url}
        Niche: {niche}
        Strategy Type: {strategy}

        Your design must include:
        1. Money Site (The target)
        2. Tier 1 Web 2.0 properties (linked to money site)
        3. Tier 2 properties (linked to Tier 1)
        4. Cross-linking structure to maximize PageRank funneling without leaving footprints.
        5. 'Link Wheel' or 'Double Link Wheel' patterns.

        Return JSON ONLY:
        {{
            "strategy_name": "{strategy.capitalize()} Link Wheel",
            "money_site": "{money_site_url}",
            "tiers": [
                {{
                    "level": 1,
                    "properties": [
                        {{ "type": "Web 2.0 (e.g. WordPress, Blogger)", "purpose": "Direct authority transfer", "links_to": "{money_site_url}" }}
                    ]
                }},
                {{
                    "level": 2,
                    "properties": [
                        {{ "type": "Social Profiles / Wiki", "purpose": "Tier 1 power-up", "links_to": "Tier 1 Properties" }}
                    ]
                }}
            ],
            "diagram_instructions": "Mermaid-style graph directions",
            "footprint_avoidance": "List of tactics to avoid detection"
        }}
        """
        return self.provider.generate_json(prompt)

    async def hunt_backlinks(self, niche, competitor_urls=None):
        """
        Finds high-power backlink targets using real search footprints.
        """
        from agents.researcher import ResearcherAgent
        researcher = ResearcherAgent()
        
        # 1. Generate Footprints
        footprints = [
            f'"{niche}" "write for us"',
            f'"{niche}" "guest post"',
            f'"{niche}" "submit an article"',
            f'"{niche}" "powered by wordpress" leave a reply',
            f'"{niche}" inurl:resources',
            f'"{niche}" intitle:"useful links"'
        ]
        
        if competitor_urls:
            # Simple competitor analysis (simulated specific check for now)
            # In a real scenario, we'd use a backlink checker API (Ahrefs/Semrush)
            # For now, we search for sites that might mention the competitor
            if isinstance(competitor_urls, str):
                competitor_urls = [competitor_urls]
            for comp in competitor_urls:
                if comp.strip():
                     footprints.append(f'"{niche}" "{comp.strip()}" -site:{comp.strip()}')

        # 2. Execute Searches
        all_targets = []
        seen_urls = set()
        
        # Limit total to avoid long wait times
        max_per_footprint = 5 
        
        for fp in footprints:
            # We use the existing mass_harvest or gather_intel from Researcher
            # Assuming mass_harvest is best for raw lists
            results = await researcher.mass_harvest(fp, num_results=max_per_footprint)
            
            for res in results:
                url = res.get('url')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    
                    # Heuristic Type Detection
                    t_type = "General"
                    lower_url = url.lower()
                    if "guest" in lower_url or "write-for" in lower_url:
                        t_type = "Guest Post"
                    elif "resource" in lower_url or "links" in lower_url:
                        t_type = "Resource Page"
                    elif "blog" in lower_url:
                        t_type = "Blog Comment"
                        
                    all_targets.append({
                        "url": url,
                        "type": t_type,
                        "authority_est": "Unknown", # Need an API for DA/DR
                        "outreach_strategy": f"Reference: {fp}",
                        "title": res.get('title', 'Unknown Title'),
                        "description": res.get('description', '')
                    })
        
        return {
            "targets": all_targets,
            "total_found": len(all_targets)
        }

    async def auto_submit_backlink(self, target_url, money_site_url, context=""):
        """
        Executes a backlink creation mission.
        - If target is a known Web 2.0 (WordPress, etc.) -> Uses SEOBridge (Article Post)
        - If target is a Blog -> Uses CommentAgent (Spun Comment)
        - Else -> Simulates outreach
        """
        from seo_bridge import seo_bridge
        from agents.comment_agent import CommentAgent
        import asyncio

        # 1. Identify Platform & Type
        detect_prompt = f"""
        Analyze this URL: {target_url}
        Determine:
        1. Platform: (wordpress, blogger, tumblr, or 'general_web')
        2. Type: (blog_post, forum, guestbook, or 'article_site')
        
        Return JSON: {{ "platform": "...", "type": "..." }}
        """
        meta = self.provider.generate_json(detect_prompt)
        platform = meta.get('platform', 'general_web').lower()
        site_type = meta.get('type', 'blog_post').lower()

        # A. KNOWN PLATFORM (Web 2.0 Article Submission)
        # SEnuke style: Post an article if we have credentials
        if platform in ['wordpress', 'blogger', 'tumblr', 'medium', 'linkedin']:
            # Generate Article Content
            article_title = f"Insights on {context}"
            article_body = self.provider.generate_text(f"Write a 300-word blog post about {context}. Include a natural link to {money_site_url} with anchor text related to {context}.")
            
            res = await seo_bridge.execute_submission(
                platform_name=platform,
                title=article_title,
                content=article_body,
                links_to=money_site_url
            )
            if res.get('status') == 'success':
                 return {"status": "success", "method_used": f"Web 2.0 Post ({platform})", "details": res}

        # B. GENERIC BLOG (Comment Submission)
        # ScrapeBox style: Blast a comment
        if site_type == 'blog_post' or platform == 'wordpress':
            comment_agent = CommentAgent()
            # Generate Spun Comment
            seed = f"Great post about {context}! I found similar info at {money_site_url}."
            spun = await comment_agent.spin_comment(seed, context=target_url)
            
            # Post
            # For "Name" and "Email", we utilize personas or randoms. 
            # In a real tool, these would be config-driven.
            res = await comment_agent.post_comment(
                target_url, 
                name="Smarketer Reader", 
                email="outreach@smarketer-pro.com", 
                website=money_site_url, 
                comment_body=spun
            )
            if res.get('status') == 'success':
                return {"status": "success", "method_used": "Blog Comment", "details": res}
            # If comment failed, fall through to simulation

        # C. FORUM / GENERIC SITE (Account Creation + Post)
        # [NEW] Enhanced Autonomous Registration
        if site_type in ['forum', 'community', 'discussion'] or platform in ['phpbb', 'vbulletin', 'xenforo']:
            from agents.account_creator import AccountCreatorAgent
            from config import get_cpanel_config
            from proxy_manager import proxy_manager
            
            # 1. Register
            cp_conf = get_cpanel_config()
            if cp_conf and cp_conf.get('url'):
                print(f"🤖 Auto-Registering on {target_url}...")
                creator = AccountCreatorAgent(cp_conf)
                
                # Use proxy
                proxy = proxy_manager.get_proxy()
                if not proxy: 
                    await proxy_manager.fetch_proxies()
                    proxy = proxy_manager.get_proxy()
                
                # Attempt Creation
                # We assume registration URL is typically /register or /signup, but Agent can find it 
                # or we just point to main URL and hope it finds the button (future improvement)
                # For now, let's assume we pass the target_url and the Agent is smart enough OR we guess /register
                reg_url = target_url.rstrip('/') + "/register" # Naive guess for now
                
                # Check if we can find a register link on the page first?
                # Ideally yes. For this MVP integration:
                create_res = await creator.create_account("ForumUser", reg_url, proxy=proxy)
                
                if "verified" in str(create_res).lower():
                     # 2. Post (Simulated for now as we don't have a ForumPoster agent yet)
                     return {
                         "status": "success", 
                         "method_used": "Auto-Registration + Post", 
                         "details": f"Created account {create_res}. Posted content (simulated)."
                     }
                else:
                     return {"status": "failed", "method_used": "Auto-Registration", "details": f"Registration failed: {create_res}"}

        # D. FALLBACK / SIMULATION -> REAL TASK
        # Instead of pretending we did it, we create a TASK for the user.
        from database import create_task
        import time
        
        task_desc = f"Manual Outreach to {target_url} for {context}"
        # Priority: High (since it was auto-scouted)
        # Type: Email/Form Fill
        create_task(
            lead_id=None, # Generic task
            description=task_desc,
            due_date=int(time.time()) + 86400, # Due in 24h
            priority="High",
            task_type="Manual Outreach"
        )

        return {
            "status": "task_created", 
            "method_used": "Task Created (Manual)", 
            "details": f"Target {target_url} identified as {site_type}. Task created for manual review."
        }

    async def run_link_wheel_mission(self, money_site_url, niche, strategy="standard", status_callback=None):
        """
        Autonomous execution of a full Link Wheel mission.
        """
        if status_callback: status_callback(f"🚀 Initializing {strategy} Link Wheel for {money_site_url}")
        
        # 1. Design the structure
        if status_callback: status_callback("🎨 Designing Tier Architecture...")
        plan = self.design_link_wheel(money_site_url, niche, strategy)
        
        results = {
            "plan": plan,
            "executions": []
        }
        
        # 2. Process Tiers
        for tier in plan.get('tiers', []):
            level = tier.get('level')
            if status_callback: status_callback(f"🏗️ Processing Tier {level}...")
            
            # Find targets for this tier
            if status_callback: status_callback(f"🔍 Hunting targets for Tier {level}...")
            targets = self.hunt_backlinks(niche)
            
            tier_executions = []
            for target in targets.get('targets', []):
                target_url = target['url']
                if status_callback: status_callback(f"  > Submitting to {target_url}...")
                
                # Determine what to link to (Money site for Tier 1, Tier 1 for Tier 2)
                links_to = money_site_url if level == 1 else "Tier 1 Properties"
                
                # Execute submission
                sub_res = await self.auto_submit_backlink(target_url, links_to, context=niche)
                tier_executions.append({
                    "target": target_url,
                    "status": sub_res.get('status'),
                    "method": sub_res.get('method_used')
                })
            
            results['executions'].append({
                "tier": level,
                "submissions": tier_executions
            })
            
        if status_callback: status_callback("✅ Link Wheel Mission Complete!")
        return results

    async def bulk_analyze_domains(self, domains, status_callback=None):
        """
        Rapidly checks a list of domains for:
        - Resolvability (DNS/HTTP)
        - HTTP Status Code
        - Page Title
        - Meta Description presence
        """
        import aiohttp
        from bs4 import BeautifulSoup
        
        results = []
        
        async with aiohttp.ClientSession() as session:
             for dom in domains:
                dom = dom.strip()
                if not dom: continue
                if not dom.startswith('http'):
                    dom = f"http://{dom}"
                
                if status_callback: status_callback(f"Checking {dom}...")
                
                try:
                    async with session.get(dom, timeout=10, allow_redirects=True, headers={"User-Agent": "Mozilla/5.0"}) as response:
                        html = await response.text()
                        
                        soup = BeautifulSoup(html, 'html.parser')
                        title = soup.title.string.strip() if soup.title else "No Title"
                        
                        results.append({
                            "url": dom,
                            "status": response.status,
                            "title": title[:50] + "..." if len(title) > 50 else title,
                            "alive": response.status < 400
                        })
                except Exception as e:
                    results.append({
                        "url": dom,
                        "status": "Error",
                        "title": str(e),
                        "alive": False
                    })
        
        return results
