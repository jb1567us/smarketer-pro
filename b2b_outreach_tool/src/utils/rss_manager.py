import datetime
import logging
import aiohttp
import asyncio

class RSSManager:
    """
    Handles generation and distribution of RSS feeds to boost indexing.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def generate_rss_xml(self, items, channel_title, channel_link, description="SEO Content Feed"):
        """
        Generates a standard RSS 2.0 XML string.
        items: List of dicts with {'title', 'link', 'description', 'pubDate'}
        """
        now = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
        
        xml = f'<?xml version="1.0" encoding="UTF-8" ?>\n'
        xml += f'<rss version="2.0">\n'
        xml += f'<channel>\n'
        xml += f'  <title>{channel_title}</title>\n'
        xml += f'  <link>{channel_link}</link>\n'
        xml += f'  <description>{description}</description>\n'
        xml += f'  <lastBuildDate>{now}</lastBuildDate>\n'
        xml += f'  <language>en-us</language>\n'

        for item in items:
            pub_date = item.get('pubDate', now)
            xml += f'  <item>\n'
            xml += f'    <title>{item["title"]}</title>\n'
            xml += f'    <link>{item["link"]}</link>\n'
            xml += f'    <description>{item["description"]}</description>\n'
            xml += f'    <pubDate>{pub_date}</pubDate>\n'
            xml += f'  </item>\n'

        xml += f'</channel>\n'
        xml += f'</rss>'
        return xml

    async def distribute_to_aggregators(self, feed_url, aggregators=None):
        """
        Executes real pings to RSS aggregators for a FEED URL.
        """
        if not aggregators:
            aggregators = [
                "http://rpc.pingomatic.com/",
                "http://rpc.twingly.com/",
                "http://api.feedburner.com/fb/a/pingSubmit",
                "http://blogsearch.google.com/ping/RPC2",
                "http://rpc.weblogs.com/RPC2",
                "http://ping.blo.gs/",
                "http://www.blogdigger.com/RPC2",
                "http://rpc.technorati.com/rpc/ping",
                "http://ping.feedburner.com",
                "http://services.newsgator.com/ngws/xmlrpcping.aspx",
                "http://valer-it.ru/rpc",
                "http://ping.syndic8.com/xmlrpc.php",
                "http://ping.bloggers.jp/rpc/",
                "http://bblog.com/ping.php",
                "http://blog.goo.ne.jp/XMLRPC",
                "http://rpc.pingomatic.com/",
                "http://api.my.yahoo.com/rss/ping",
                "http://api.my.yahoo.com/RPC2"
            ]
        
        results = []
        async with aiohttp.ClientSession() as session:
            for aggregator in aggregators:
                try:
                    # Some use GET, some use POST with 'url' param
                    target = f"{aggregator}?url={feed_url}" if "?" not in aggregator else f"{aggregator}&url={feed_url}"
                    async with session.get(target, timeout=10) as response:
                        status = "success" if response.status < 400 else f"failed ({response.status})"
                        results.append({"aggregator": aggregator, "status": status})
                except Exception as e:
                    results.append({"aggregator": aggregator, "status": f"error: {str(e)}"})
        
        return results

    async def ping_url(self, target_url):
        """
        Simple pinger for a single URL.
        """
        return await self.distribute_to_aggregators(target_url)

    async def run_rss_mission(self, urls, niche):
        """
        Full workflow: Take URLs, generate feed, and distribute.
        """
        items = []
        for i, url in enumerate(urls):
            items.append({
                "title": f"New content on {niche} - Part {i+1}",
                "link": url,
                "description": f"Check out this latest update on {niche}."
            })
        
        feed_xml = self.generate_rss_xml(
            items, 
            channel_title=f"{niche.capitalize()} SEO Feed", 
            channel_link=urls[0] if urls else "http://example.com",
            description=f"Automated SEO feed for {niche} niche."
        )
        
        distribution = await self.distribute_to_aggregators(feed_xml)
        return {
            "feed_xml": feed_xml,
            "distribution_results": distribution
        }
