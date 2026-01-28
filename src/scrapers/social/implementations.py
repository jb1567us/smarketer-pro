from scrapers.social.base import BaseSocialScraper
import json
import re

class TwitterScraper(BaseSocialScraper):
    def construct_url(self, handle):
        return f"https://twitter.com/{handle.replace('@', '')}"

    async def try_browser_scrape(self, url, platform):
        # We need to override to setup listener BEFORE goto
        # Implementation similar to base but with listener
        return await super().try_browser_scrape(url, platform)

    async def platform_extract(self, page, content):
        # Setup listener handled in override if needed, 
        # but for simplicity, let's just use the base for now 
        #and move specific intercept logic here if we can.
        return {}

class InstagramScraper(BaseSocialScraper):
    def construct_url(self, handle):
        return f"https://instagram.com/{handle.replace('@', '')}"

class ThreadsScraper(BaseSocialScraper):
    def construct_url(self, handle):
        return f"https://www.threads.net/@{handle.replace('@', '')}"

    async def platform_extract(self, page, content):
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        scripts = soup.find_all('script', attrs={"type": "application/json", "data-sjs": True})
        for s in scripts:
            if "follower_count" in s.text:
                try:
                    return {"threads_json": json.loads(s.text)}
                except: continue
        return {}

class TikTokScraper(BaseSocialScraper):
    def construct_url(self, handle):
        return f"https://tiktok.com/@{handle.replace('@', '')}"

class LinkedInScraper(BaseSocialScraper):
    def construct_url(self, handle):
        return f"https://linkedin.com/in/{handle.replace('@', '')}"

class RedditScraper(BaseSocialScraper):
    def construct_url(self, handle):
        """Construct Reddit user or subreddit URL."""
        # Detect if it's a subreddit (starts with r/) or user
        if handle.startswith('r/') or handle.startswith('/r/'):
            # Extract just the subreddit name
            clean_handle = handle.replace('/r/', '').replace('r/', '').replace('@', '')
            return f"https://reddit.com/r/{clean_handle}"
        
        # User profile
        clean_handle = handle.replace('@', '').replace('u/', '').replace('/u/', '')
        return f"https://reddit.com/user/{clean_handle}"
    
    async def platform_extract(self, page, content):
        """Extract Reddit-specific data from page."""
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        
        # Try to find karma in various locations
        data = {}
        
        # Look for JSON data in script tags
        scripts = soup.find_all('script', id='data')
        for script in scripts:
            if 'karma' in script.text.lower():
                try:
                    json_data = json.loads(script.text)
                    data['reddit_json'] = json_data
                except:
                    pass
        
        # Extract visible stats from text
        text = soup.get_text()
        if 'karma' in text.lower():
            # Try to find karma numbers
            karma_match = re.search(r'(\d{1,3}(?:,\d{3})*|\d+)\s*(?:post\s*)?karma', text, re.IGNORECASE)
            if karma_match:
                data['karma'] = karma_match.group(1)
        
        return data

class YouTubeScraper(BaseSocialScraper):
    def construct_url(self, handle):
        """Construct YouTube channel URL."""
        clean_handle = handle.replace('@', '')
        
        # Handle different YouTube URL formats
        if handle.startswith('UC'):  # Channel ID format
            return f"https://youtube.com/channel/{clean_handle}"
        elif '/c/' in handle:
            # Extract channel name after /c/
            clean_handle = handle.split('/c/')[-1]
            return f"https://youtube.com/c/{clean_handle}"
        elif handle.startswith('c/'):
            clean_handle = handle.replace('c/', '')
            return f"https://youtube.com/c/{clean_handle}"
        else:  # Modern @handle format
            return f"https://youtube.com/@{clean_handle}"
    
    async def platform_extract(self, page, content):
        """Extract YouTube-specific data from page."""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(content, 'html.parser')
        data = {}
        
        # YouTube embeds data in script tags as JSON
        scripts = soup.find_all('script')
        for script in scripts:
            if not script.string:
                continue
            
            # Look for ytInitialData
            if 'ytInitialData' in script.string:
                try:
                    # Extract JSON from var ytInitialData = {...};
                    json_match = re.search(r'var ytInitialData = ({.*?});', script.string)
                    if json_match:
                        yt_data = json.loads(json_match.group(1))
                        data['youtube_data'] = yt_data
                        
                        # Try to extract subscriber count from nested structure
                        try:
                            header = yt_data.get('header', {}).get('c4TabbedHeaderRenderer', {})
                            sub_text = header.get('subscriberCountText', {}).get('simpleText', '')
                            if sub_text:
                                data['subscribers'] = sub_text
                        except:
                            pass
                except:
                    pass
        
        # Fallback: look for meta tags
        meta_desc = soup.find('meta', property='og:description')
        if meta_desc:
            data['meta_description'] = meta_desc.get('content', '')
        
        return data

class PinterestScraper(BaseSocialScraper):
    def construct_url(self, handle):
        """Construct Pinterest profile URL."""
        clean_handle = handle.replace('@', '').strip('/')
        return f"https://pinterest.com/{clean_handle}"
    
    async def platform_extract(self, page, content):
        """Extract Pinterest-specific data from page."""
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(content, 'html.parser')
        data = {}
        
        # Pinterest often has stats in meta tags
        meta_desc = soup.find('meta', property='og:description')
        if meta_desc:
            desc = meta_desc.get('content', '')
            data['meta_description'] = desc
            
            # Extract follower count from description
            # Format: "123K followers, 456 following"
            follower_match = re.search(r'([\d,.]+[KkMm]?)\s*followers', desc, re.IGNORECASE)
            following_match = re.search(r'([\d,.]+[KkMm]?)\s*following', desc, re.IGNORECASE)
            
            if follower_match:
                data['followers'] = follower_match.group(1)
            if following_match:
                data['following'] = following_match.group(1)
        
        # Look for JSON-LD structured data
        json_ld = soup.find('script', type='application/ld+json')
        if json_ld:
            try:
                ld_data = json.loads(json_ld.string)
                if isinstance(ld_data, dict):
                    data['json_ld'] = ld_data
            except:
                pass
        
        return data
