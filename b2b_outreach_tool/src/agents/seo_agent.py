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

    def audit_site(self, url):
        return self.run(f"Perform a technical SEO audit for the website: {url}")

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

    def hunt_backlinks(self, niche, competitor_urls=None):
        """
        Finds high-power backlink targets.
        """
        comp_str = f" based on competitors: {competitor_urls}" if competitor_urls else ""
        prompt = f"""
        Find 10 high-authority backlink opportunities for the niche '{niche}'{comp_str}.
        Look for:
        - Guest post targets
        - Resource pages
        - Broken link opportunities
        - Competitor backlink clones

        Return JSON ONLY:
        {{
            "targets": [
                {{ "url": "", "type": "Guest Post/Resource/etc", "authority_est": "High/Med", "outreach_strategy": "" }}
            ],
            "total_found": 10
        }}
        """
        return self.provider.generate_json(prompt)

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

        # C. FALLBACK / SIMULATION
        return {
            "status": "simulated_success", 
            "method_used": "Manual Outreach (Simulated)", 
            "details": f"Target {target_url} identified as {site_type}. Added to outreach queue."
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
