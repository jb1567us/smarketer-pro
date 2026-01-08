from .base import BaseAgent
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import urllib.parse

class CommentAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            role="Mass Commenter & Engager",
            goal="Automate high-quality blog commenting to build relationships and backlinks.",
            provider=provider
        )

    async def spin_comment(self, seed_comment, context=None):
        """
        Generates a unique variation of the comment using LLM.
        """
        prompt = f"""
        Rewrite the following blog comment to be unique but keep the same meaning.
        Make it sound natural and human.
        
        Seed Comment: "{seed_comment}"
        Context (optional): {context}
        
        Return ONLY the rewritten comment text.
        """
        return self.provider.generate_text(prompt)

    async def post_comment(self, target_url, name, email, website, comment_body):
        """
        Attempts to post a comment to the target URL.
        """
        result = {}
        # 1. Fetch page to find form
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(target_url, timeout=10) as response:
                    if response.status != 200:
                        result = {"status": "failed", "reason": f"HTTP {response.status}"}
                    else:
                        html = await response.text()
                        
                        # 2. Parse form
                        soup = BeautifulSoup(html, 'html.parser')
                        form = self.find_comment_form(soup)
                        
                        if not form:
                            result = {"status": "failed", "reason": "No comment form found"}
                        else:
                            # 3. Prepare data
                            action = form.get('action')
                            if not action:
                                action = target_url # Post to self if no action
                            elif not action.startswith('http'):
                                action = urllib.parse.urljoin(target_url, action)
                                
                            data = {}
                            inputs = form.find_all('input')
                            textareas = form.find_all('textarea')
                            
                            # Intelligent field mapping
                            for inp in inputs:
                                if not inp.get('name'): continue
                                name_attr = inp.get('name').lower()
                                
                                if 'name' in name_attr or 'author' in name_attr:
                                    data[inp['name']] = name
                                elif 'email' in name_attr:
                                    data[inp['name']] = email
                                elif 'url' in name_attr or 'website' in name_attr:
                                    data[inp['name']] = website
                                elif 'submit' in name_attr:
                                    data[inp['name']] = inp.get('value', 'Submit')
                                else:
                                    # Hidden fields, nonces, etc.
                                    if inp.get('value'):
                                        data[inp['name']] = inp['value']
                                        
                            for ta in textareas:
                                name_attr = ta.get('name', '').lower()
                                if 'comment' in name_attr or 'message' in name_attr:
                                    data[ta['name']] = comment_body
            
                            # 4. Submit
                            async with session.post(action, data=data, timeout=15) as post_response:
                                if post_response.status == 200:
                                    # Check for success indicators
                                    res_text = await post_response.text()
                                    if "moderation" in res_text.lower() or "awaiting" in res_text.lower():
                                         result = {"status": "success", "detail": "Comment awaiting moderation"}
                                    else:
                                         result = {"status": "success", "detail": f"Posted to {action}"}
                                else:
                                    result = {"status": "failed", "reason": f"Post failed {post_response.status}"}
                                    
        except Exception as e:
            result = {"status": "error", "reason": str(e)}
            
        self.save_work_product(str(result), task_instruction=f"Post comment to {target_url}", tags=["comment", "outreach"])
        return result

    def find_comment_form(self, soup):
        """
        Heuristic to find the main comment form.
        """
        forms = soup.find_all('form')
        for f in forms:
            cls = f.get('class', [])
            fid = f.get('id', '')
            # Check ID/Class
            if 'comment' in str(fid).lower() or 'comment' in str(cls).lower():
                return f
            # Check action
            action = f.get('action', '')
            if 'wp-comments-post' in action:
                return f
        return None
