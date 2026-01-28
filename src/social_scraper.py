import asyncio
from scrapers.social.implementations import (
    TwitterScraper, InstagramScraper, ThreadsScraper, 
    TikTokScraper, LinkedInScraper, RedditScraper, YouTubeScraper,
    PinterestScraper, BaseSocialScraper
)
from scrapers.social.utils import parse_social_stats

VALID_PLATFORMS = ["twitter", "linkedin", "tiktok", "instagram", "reddit", "youtube", "threads", "pinterest"]

class SocialScraper:
    """
    Modular Facade for Social Media Scrapers.
    Delegates to platform-specific implementations.
    """
    def __init__(self):
        self.scrapers = {
            "twitter": TwitterScraper(),
            "instagram": InstagramScraper(),
            "threads": ThreadsScraper(),
            "tiktok": TikTokScraper(),
            "linkedin": LinkedInScraper(),
            "reddit": RedditScraper(),
            "youtube": YouTubeScraper(),
            "pinterest": PinterestScraper(),
            "default": BaseSocialScraper()
        }

    async def close(self):
        for s in self.scrapers.values():
            await s.close()

    async def smart_scrape(self, query_or_url, platform=None):
        if not platform and query_or_url.startswith("http"):
            platform = self._detect_platform(query_or_url)
        
        if not platform:
            return {"error": "Could not detect platform. Please specify one."}

        scraper = self.scrapers.get(platform, self.scrapers["default"])
        print(f"  [SocialScraper] Delegating to {scraper.__class__.__name__} for {platform}")
        return await scraper.smart_scrape(query_or_url, platform)

    def _detect_platform(self, url):
        u = url.lower()
        if "linkedin.com" in u: return "linkedin"
        if "twitter.com" in u or "x.com" in u: return "twitter"
        if "tiktok.com" in u: return "tiktok"
        if "instagram.com" in u: return "instagram"
        if "reddit.com" in u: return "reddit"
        if "youtube.com" in u: return "youtube"
        if "threads.net" in u: return "threads"
        if "pinterest.com" in u: return "pinterest"
        return None

    def _construct_url(self, platform, handle):
        scraper = self.scrapers.get(platform, self.scrapers["default"])
        return scraper.construct_url(handle)
