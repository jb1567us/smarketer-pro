import asyncio
import aiohttp
import base64
import os
import time
from .local_whisper import LocalWhisperSolver

class CaptchaSolver:
    def __init__(self, provider, api_key, custom_url=None):
        self.provider = provider.lower()
        self.api_key = api_key
        self.custom_url = custom_url
        self.enabled = bool((api_key or self.provider == "xevil") and self.provider != "none")

    async def solve_recaptcha_v2(self, site_key, page_url):
        """Solves reCAPTCHA v2 using the configured provider."""
        if not self.enabled:
            return {"error": "Captcha solver disabled or not configured"}

        providers = {
            "2captcha": self._solve_2captcha_recaptcha,
            "xevil": self._solve_xevil_recaptcha,
            "anticaptcha": self._solve_anticaptcha_recaptcha,
            "deathbycaptcha": self._solve_deathbycaptcha_recaptcha,
            "capsolver": self._solve_capsolver_recaptcha,
            "bestcaptchasolver": self._solve_bestcaptchasolver_recaptcha,
            "local-whisper": self._solve_local_whisper
        }
        
        handler = providers.get(self.provider)
        if handler:
            return await handler(site_key, page_url)
        
        return {"error": f"Provider {self.provider} not supported Yet"}

    async def _solve_2captcha_recaptcha(self, site_key, page_url):
        """Implementation for 2Captcha reCAPTCHA v2."""
        base_url = "http://2captcha.com"
        return await self._solve_2captcha_compatible(base_url, site_key, page_url)

    async def _solve_xevil_recaptcha(self, site_key, page_url):
        """Implementation for XEvil (emulating 2Captcha)."""
        base_url = self.custom_url or "http://127.0.0.1"
        return await self._solve_2captcha_compatible(base_url, site_key, page_url)

    async def _solve_2captcha_compatible(self, base_url, site_key, page_url):
        """Generic 2Captcha-compatible API solver (used by 2Captcha and XEvil)."""
        async with aiohttp.ClientSession() as session:
            submit_url = f"{base_url}/in.php?key={self.api_key}&method=userrecaptcha&googlekey={site_key}&pageurl={page_url}&json=1"
            async with session.get(submit_url) as resp:
                try:
                    data = await resp.json()
                except:
                    # Fallback for plain text responses (XEvil sometimes does this)
                    text = await resp.text()
                    if "OK|" in text:
                        data = {"status": 1, "request": text.split("|")[1]}
                    else:
                        return {"error": f"API Error: {text}"}

                if data.get("status") != 1:
                    return {"error": f"API error: {data.get('request')}"}
                request_id = data.get("request")

            result_url = f"{base_url}/res.php?key={self.api_key}&action=get&id={request_id}&json=1"
            for _ in range(30):
                await asyncio.sleep(5)
                async with session.get(result_url) as resp:
                    try:
                        data = await resp.json()
                    except:
                        text = await resp.text()
                        if "OK|" in text:
                            data = {"status": 1, "request": text.split("|")[1]}
                        elif text == "CAPCHA_NOT_READY":
                            data = {"status": 0, "request": "CAPCHA_NOT_READY"}
                        else:
                            return {"error": f"API Error: {text}"}

                    if data.get("status") == 1:
                        return {"status": "success", "token": data.get("request")}
                    elif data.get("request") == "CAPCHA_NOT_READY":
                        continue
                    else:
                        return {"error": f"API error: {data.get('request')}"}
            return {"error": "Timeout"}

    async def _solve_anticaptcha_recaptcha(self, site_key, page_url):
        """Implementation for Anti-Captcha reCAPTCHA v2."""
        url = "https://api.anti-captcha.com/createTask"
        payload = {
            "clientKey": self.api_key,
            "task": {
                "type": "NoCaptchaTaskProxyless",
                "websiteURL": page_url,
                "websiteKey": site_key
            }
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                data = await resp.json()
                if data.get("errorId") != 0:
                    return {"error": f"Anti-Captcha error: {data.get('errorDescription')}"}
                task_id = data.get("taskId")

            res_url = "https://api.anti-captcha.com/getTaskResult"
            for _ in range(30):
                await asyncio.sleep(5)
                async with session.post(res_url, json={"clientKey": self.api_key, "taskId": task_id}) as resp:
                    data = await resp.json()
                    if data.get("status") == "ready":
                        return {"status": "success", "token": data.get("solution", {}).get("gRecaptchaResponse")}
                    elif data.get("errorId") != 0:
                        return {"error": f"Anti-Captcha error: {data.get('errorDescription')}"}
            return {"error": "Timeout"}

    async def _solve_capsolver_recaptcha(self, site_key, page_url):
        """Implementation for CapSolver reCAPTCHA v2."""
        url = "https://api.capsolver.com/createTask"
        payload = {
            "clientKey": self.api_key,
            "task": {
                "type": "ReCaptchaV2TaskProxyless",
                "websiteURL": page_url,
                "websiteKey": site_key
            }
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                data = await resp.json()
                if data.get("errorId") != 0:
                    return {"error": f"CapSolver error: {data.get('errorDescription')}"}
                task_id = data.get("taskId")

            res_url = "https://api.capsolver.com/getTaskResult"
            for _ in range(30):
                await asyncio.sleep(5)
                async with session.post(res_url, json={"clientKey": self.api_key, "taskId": task_id}) as resp:
                    data = await resp.json()
                    if data.get("status") == "ready":
                        return {"status": "success", "token": data.get("solution", {}).get("gRecaptchaResponse")}
            return {"error": "Timeout"}

    async def _solve_deathbycaptcha_recaptcha(self, site_key, page_url):
        """Simplistic placeholder for DeathByCaptcha (uses login/pass usually)."""
        return {"error": "DeathByCaptcha requires unique credentials format (User:Pass). Not fully implemented."}

    async def _solve_bestcaptchasolver_recaptcha(self, site_key, page_url):
        """Placeholder for BestCaptchaSolver."""
        return {"error": "BestCaptchaSolver not yet implemented."}

    async def _solve_local_whisper( self, site_key, page_url, audio_url=None):
        """
        Solves using local Whisper. 
        NOTE: Requires audio_url to be passed directly or extracted.
        """
        if not audio_url:
            return {"error": "Local Whisper requires audio_url. Please ensure the automation extracts the audio challenge link."}
        
        solver = LocalWhisperSolver()
        return await solver.solve_audio(audio_url)

    async def get_balance(self):
        """Retrieves the current balance from the provider."""
        if not self.enabled:
            return None

        async with aiohttp.ClientSession() as session:
            try:
                if self.provider == "2captcha":
                    url = f"http://2captcha.com/res.php?key={self.api_key}&action=getbalance&json=1"
                    async with session.get(url) as resp:
                        data = await resp.json()
                        if data.get("status") == 1: return f"${data.get('request')}"
                elif self.provider == "anticaptcha":
                    url = "https://api.anti-captcha.com/getBalance"
                    async with session.post(url, json={"clientKey": self.api_key}) as resp:
                        data = await resp.json()
                        if data.get("errorId") == 0: return f"${data.get('balance')}"
                elif self.provider == "capsolver":
                    url = "https://api.capsolver.com/getBalance"
                    async with session.post(url, json={"clientKey": self.api_key}) as resp:
                        data = await resp.json()
                        if data.get("errorId") == 0: return f"${data.get('balance')}"
            except:
                pass
            return "N/A"
