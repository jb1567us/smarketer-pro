from .base import BaseAgent
import asyncio
import random
from datetime import datetime

class SocialListeningAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            role="Social Media Guardian",
            goal="Monitor social platforms for brand mentions, competitor weakness, and high-intent buying signals.",
            provider=provider
        )

    async def listen_for_keywords(self, keywords, platforms=None):
        """
        Simulates listening on social platforms. 
        In a production env, this would hook into Twitter API v2 / LinkedIn API.
        """
        if not platforms:
            platforms = ["twitter", "linkedin", "reddit"]
            
        found_signals = []
        
        for kw in keywords:
            # Simulate fetching posts
            raw_posts = await self._fetch_posts_mock(kw, platforms)
            
            # Analyze sentiment and intent
            for post in raw_posts:
                analysis = await self.analyze_signal(post['content'], kw)
                if analysis.get('is_relevant'):
                    post['analysis'] = analysis
                    found_signals.append(post)
                    
        return found_signals

    async def analyze_signal(self, content, keyword):
        """
        Uses LLM to determine if a post is a 'Warm Lead'.
        """
        prompt = f"""
        Analyze this social media post for buying intent or pain points related to '{keyword}'.
        
        Post: "{content}"
        
        Return JSON ONLY:
        {{
            "is_relevant": true/false,
            "sentiment": "positive/negative/neutral",
            "intent_score": 1-10,
            "classification": "Competitor Complaint / Buying Signal / General Discussion",
            "suggested_reply_angle": "Brief tip on how to reply"
        }}
        """
        return self.provider.generate_json(prompt)

    async def _fetch_posts_mock(self, keyword, platforms):
        """
        Generates realistic mock data for demonstration.
        """
        mock_templates = [
            "Does anyone know a good alternative to {competitor}? Their support is terrible.",
            "I'm struggling with {topic}. Any tool recommendations?",
            "Just launched my new agency but finding {topic} really hard to scale.",
            "Looking for a {topic} expert to help with our Q3 goals. DM me.",
            "Why is {topic} so complicated? I just want a simple dashboard.",
            "Has anyone tried {competitor}? Thinking of switching."
        ]
        
        competitors = ["Salesforce", "HubSpot", "Outreach.io", "Lemlist"]
        
        posts = []
        # Generate 3-5 random posts per keyword
        result_count = random.randint(3, 5)
        
        for _ in range(result_count):
            tpl = random.choice(mock_templates)
            content = tpl.format(topic=keyword, competitor=random.choice(competitors))
            
            platform = random.choice(platforms)
            user = f"User_{random.randint(1000, 9999)}"
            
            posts.append({
                "platform": platform,
                "user": user,
                "content": content,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "url": f"https://{platform}.com/{user}/status/{random.randint(100000, 999999)}"
            })
            
        return posts

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
