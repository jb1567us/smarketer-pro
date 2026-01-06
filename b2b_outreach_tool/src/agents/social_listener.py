from .base import BaseAgent
import asyncio
import random
from datetime import datetime
import aiohttp
from scraper import search_searxng

class SocialListeningAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            role="Social Media Guardian",
            goal="Monitor social platforms for brand mentions, competitor weakness, and high-intent buying signals.",
            provider=provider
        )

    async def listen_for_keywords(self, keywords, platforms=None, num_results=5):
        """
        Listens on social platforms using SearXNG.
        """
        if not platforms:
            platforms = ["twitter", "linkedin", "reddit"]
            
        found_signals = []
        
        async with aiohttp.ClientSession() as session:
            for kw in keywords:
                for platform in platforms:
                    # Construct query for specific platform
                    site_operator = ""
                    if platform.lower() == "twitter":
                        site_operator = "site:twitter.com"
                    elif platform.lower() == "linkedin":
                        site_operator = "site:linkedin.com/posts"
                    elif platform.lower() == "reddit":
                        site_operator = "site:reddit.com"
                    
                    query = f"{site_operator} {kw}"
                    
                    try:
                        # Fetch real results
                        results = await search_searxng(query, session, num_results=num_results)
                        
                        # Process and analyze each result
                        for result in results:
                            post = {
                                "platform": platform,
                                "user": "Unknown", # difficult to extract from snippet reliably without deep scraping
                                "content": f"{result['title']} - {result.get('url', '')}", # Title usually contains the tweet/post snippet
                                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "url": result['url']
                            }
                            
                            analysis = await self.analyze_signal(post['content'], kw)
                            if analysis.get('is_relevant'):
                                post['analysis'] = analysis
                                found_signals.append(post)
                                
                    except Exception as e:
                        print(f"Error searching for {kw} on {platform}: {e}")
        
        # Anti-Hallucination: If no signals found, return explicit empty state or special signal
        if not found_signals:
            return [{"platform": "system", "user": "System", "content": "NO_DATA_FOUND", "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"), "url": "#", "analysis": {"is_relevant": False}}]
        
        # Save work product
        if found_signals:
            self.save_work_product(
                content=found_signals, 
                task_instruction=f"Listen for keywords: {keywords}", 
                tags=["social_listening", "signals"]
            )
            
        return found_signals

    async def analyze_signal(self, content, keyword):
        """
        Uses LLM to determine if a post is a 'Warm Lead'.
        """
        prompt = f"""
        You are a Sales Intelligence Agent. Your job is to filter social media posts for high-quality buying signals while ignoring general noise.
        
        Keyword Monitored: "{keyword}"
        Post Content: "{content}"
        
        Classify the intent carefully:
        - "Buying Signal": Explicit purchase intent (e.g., "looking for...", "recommend a tool", "how do I..."). Intent Score: 8-10.
        - "Competitor Complaint": Negative sentiment towards a rival (e.g., "I hate Brand X", "Brand Y is too expensive"). Intent Score: 7-9.
        - "General Discussion": Industry news, tips, or self-promotion. Intent Score: 1-4.

        CRITICAL FILTERING RULES:
        1. IGNORE posts that appear to be written BY the brand/competitor itself (e.g., marketing announcements, official support replies). Mark these as is_relevant: false.
        2. We are ONLY interested in potential CUSTOMERS or USERS.
        
        Return JSON ONLY:
        {{
            "is_relevant": true,  // Set to FALSE if it is a marketing post from the brand itself
            "sentiment": "positive/negative/neutral",
            "intent_score": 1-10, // 10 = Cash in hand, 1 = Noise
            "classification": "Competitor Complaint / Buying Signal / General Discussion",
            "suggested_reply_angle": "Draft a helpful, non-salesy insight that gently positions us as the expert/solution."
        }}
        """
        return self.provider.generate_json(prompt)

    def generate_reply(self, post_content, angle):
        """
        Drafts a reply based on the analysis.
        """
        prompt = f"""
        Draft a short, helpful, and non-salesy social media reply to this post.
        
        Post: "{post_content}"
        Strategy: {angle}
        
        Keep it under 280 characters.
        """
        return self.provider.generate_text(prompt)
