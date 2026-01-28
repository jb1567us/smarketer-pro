import aiohttp
import asyncio
import time
import random
from config import config

class ProxyValidator:
    def __init__(self, stats_ref=None):
        self.stats = stats_ref or {
            "is_active": False,
            "total": 0,
            "checked": 0,
            "found": 0,
            "found_elite": 0,
            "found_standard": 0,
            "start_time": 0,
            "etr": 0
        }

    async def verify_batch(self, proxy_list, verbose=False):
        working_proxies = []
        concurrency = config.get("proxies", {}).get("harvest_concurrency", 50)
        batch_size = config.get("proxies", {}).get("harvest_batch_size", 1000)
        semaphore = asyncio.Semaphore(concurrency)
        
        self.stats.update({
            "is_active": True,
            "total": len(proxy_list),
            "checked": 0,
            "found": 0,
            "found_elite": 0,
            "found_standard": 0,
            "start_time": time.time()
        })
        
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
        connector = aiohttp.TCPConnector(limit=concurrency * 2, ssl=False, force_close=True) 
        
        async with aiohttp.ClientSession(headers=headers, connector=connector) as session:
            async def check(proxy):
                try:
                    async with semaphore:
                        tier = await self.verify_proxy(proxy, session=session)
                        self.stats["checked"] += 1
                        if tier > 0:
                            tier_label = "elite" if tier == 2 else "standard"
                            working_proxies.append({"address": proxy, "tier": tier_label})
                            self.stats["found"] += 1
                            if tier == 2:
                                self.stats["found_elite"] += 1
                            else:
                                self.stats["found_standard"] += 1
                        
                        elapsed = time.time() - self.stats["start_time"]
                        if self.stats["checked"] > 0:
                            speed = self.stats["checked"] / elapsed
                            remaining = self.stats["total"] - self.stats["checked"]
                            self.stats["etr"] = int(remaining / speed) if speed > 0 else 0
                        
                        if verbose:
                             status_icon = "🟢" if tier > 0 else "🔴"
                             tier_str = "ELITE" if tier == 2 else ("STANDARD" if tier == 1 else "DEAD")
                             print(f"[{self.stats['checked']}/{self.stats['total']}] {status_icon} {proxy:<21} -> {tier_str}", flush=True)

                except Exception:
                    self.stats["checked"] += 1

            for i in range(0, len(proxy_list), batch_size):
                batch = proxy_list[i:i + batch_size]
                await asyncio.gather(*(check(p) for p in batch))
                await asyncio.sleep(0.01)
                
        self.stats["is_active"] = False
        return working_proxies

    async def verify_proxy(self, proxy, session=None):
        """
        Optimized proxy verification with early termination and efficient elite check.
        Returns: 0 (dead), 1 (standard), 2 (elite)
        """
        proxy_url = proxy if proxy.startswith("http") else f"http://{proxy}"
        should_close = False
        if session is None:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
            session = aiohttp.ClientSession(headers=headers, connector=aiohttp.TCPConnector(ssl=False))
            should_close = True

        try:
            # Progressive timeout: fail fast on slow proxies
            base_timeout = aiohttp.ClientTimeout(total=8, connect=4)
            
            # 1. Quick Google Check (fastest, most forgiving)
            try:
                async with session.get(
                    "https://www.google.com/search?q=test", 
                    proxy=proxy_url, 
                    timeout=base_timeout, 
                    ssl=False
                ) as resp:
                    if resp.status == 200:
                        # Early success! Continue to elite check
                        return await self._check_elite_tier(session, proxy_url)
            except asyncio.TimeoutError:
                return 0  # Fail fast on slow proxies
            except:
                pass  # Try next engine

            # 2. DDG Check (if Google failed)
            try:
                async with session.post(
                    "https://html.duckduckgo.com/html/", 
                    data={'q': 'test'}, 
                    proxy=proxy_url, 
                    timeout=base_timeout, 
                    ssl=False
                ) as resp:
                    if resp.status in [200, 302]:
                        return await self._check_elite_tier(session, proxy_url)
                    elif resp.status == 403:
                        return 0  # Blocked, don't waste time
            except asyncio.TimeoutError:
                return 0
            except:
                pass

        except:
            pass
        finally:
            if should_close:
                await session.close()
        return 0

    async def _check_elite_tier(self, session, proxy_url):
        """
        Efficient elite tier check using HEAD request.
        Returns: 1 (standard) or 2 (elite)
        """
        try:
            # Use HEAD instead of GET to avoid downloading full page
            async with session.head(
                "https://www.instagram.com", 
                proxy=proxy_url, 
                timeout=aiohttp.ClientTimeout(total=5),  # Shorter timeout for elite check
                ssl=False,
                allow_redirects=True
            ) as ig_resp:
                if ig_resp.status == 200:
                    server = ig_resp.headers.get("Server", "").lower()
                    # Elite = bypasses Cloudflare
                    if "cloudflare" not in server:
                        return 2  # ELITE
        except:
            pass  # Failed elite check, but proxy works
        return 1  # STANDARD
