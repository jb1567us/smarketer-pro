from .base import BaseAgent
import requests
import base64
import json
import asyncio
import os

class WordPressAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            role="WordPress Expert",
            goal="Assist with WordPress installations and manage content via the REST API.",
            provider=provider
        )

    def generate_install_config(self, project_name="my_wordpress"):
        """
        Generates a docker-compose.yaml template for WordPress installation.
        """
        config_template = f"""
version: '3.8'

services:
  db:
    image: mariadb:10.6
    command: '--default-authentication-plugin=mysql_native_password'
    volumes:
      - db_data:/var/lib/mysql
    restart: always
    environment:
      - MYSQL_ROOT_PASSWORD=somewordpress
      - MYSQL_DATABASE=wordpress
      - MYSQL_USER=wordpress
      - MYSQL_PASSWORD=wordpress

  wordpress:
    image: wordpress:latest
    ports:
      - 8080:80
    restart: always
    environment:
      - WORDPRESS_DB_HOST=db
      - WORDPRESS_DB_USER=wordpress
      - WORDPRESS_DB_PASSWORD=wordpress
      - WORDPRESS_DB_NAME=wordpress
    volumes:
      - wordpress_data:/var/var/www/html

volumes:
  db_data:
  wordpress_data:
"""
        return config_template.strip()

    def _get_headers(self, username, app_password):
        """
        Helper to create Auth headers for REST API.
        """
        auth_string = f"{username}:{app_password}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        return {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/json"
        }

    async def manage_content(self, site_url, username, app_password, action, data=None):
        """
        Site Management via REST API.
        Actions: list_posts, create_post, delete_post
        """
        base_url = site_url.rstrip('/') + "/wp-json/wp/v2"
        headers = self._get_headers(username, app_password)

        try:
            if action == "list_posts":
                resp = requests.get(f"{base_url}/posts", headers=headers, timeout=15)
                return resp.json()

            elif action == "create_post":
                # data should have 'title', 'content', 'status' (default 'draft')
                payload = {
                    "title": data.get('title', 'Untitled'),
                    "content": data.get('content', ''),
                    "status": data.get('status', 'draft')
                }
                resp = requests.post(f"{base_url}/posts", headers=headers, json=payload, timeout=15)
                return resp.json()

            elif action == "delete_post":
                post_id = data.get('id')
                if not post_id:
                    return {"error": "Missing post ID"}
                resp = requests.delete(f"{base_url}/posts/{post_id}", headers=headers, timeout=15)
                return resp.json()
            
            elif action == "create_page":
                payload = {
                    "title": data.get('title', 'Untitled Page'),
                    "content": data.get('content', ''),
                    "status": data.get('status', 'draft')
                }
                resp = requests.post(f"{base_url}/pages", headers=headers, json=payload, timeout=15)
                return resp.json()

            else:
                return {"error": f"Unsupported action: {action}"}

        except Exception as e:
            return {"error": str(e)}

    async def automate_app_password(self, admin_url, username, password):
        """
        Uses Playwright to log into WordPress and generate an Application Password.
        """
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            return {"error": "Playwright not installed. Please run 'playwright install'"}

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            try:
                # 1. Login
                login_url = admin_url.rstrip('/') + "/wp-login.php"
                await page.goto(login_url)
                await page.fill("#user_login", username)
                await page.fill("#user_pass", password)
                await page.click("#wp-submit")
                await page.wait_for_load_state("networkidle")

                # 2. Navigate to Profile
                profile_url = admin_url.rstrip('/') + "/profile.php"
                await page.goto(profile_url)

                # 3. Generate App Password
                # Look for the section
                await page.scroll_into_view_if_needed("#application-passwords-section")
                app_name = "B2B_Outreach_Tool"
                await page.fill("#new_application_password_name", app_name)
                await page.click("#do_new_application_password")
                
                # Wait for the result
                await page.wait_for_selector(".new-application-password-code")
                password_code = await page.inner_text(".new-application-password-code")
                
                await browser.close()
                return {"app_password": password_code.strip(), "username": username}

            except Exception as e:
                await browser.close()
                return {"error": f"Automation failed: {str(e)}"}

    async def cpanel_install_wp(self, cpanel_url, cp_user, cp_pass, domain):
        """
        Uses Playwright to log into cPanel and install WordPress via Softaculous.
        """
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            return {"error": "Playwright not installed."}

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                # 1. cPanel Login
                await page.goto(cpanel_url)
                await page.fill("#user", cp_user)
                await page.fill("#pass", cp_pass)
                await page.click("#login_submit")
                await page.wait_for_load_state("networkidle")

                # 2. Find Softaculous/WordPress Manager
                # This part is tricky as cPanel UIs vary. We'll search for 'WordPress'
                await page.fill("#filter", "WordPress")
                await asyncio.sleep(2) # Wait for filter
                
                # Click the first match (usually WordPress Manager or Softaculous)
                await page.click("text=WordPress Manager by Softaculous")
                await page.wait_for_load_state("networkidle")

                # 3. Trigger Install
                await page.click("text=Install")
                await page.wait_for_load_state("networkidle")

                # 4. Fill Install Form (Simplified)
                # We'll assume default settings for now, just setting the domain
                # Softaculous often uses an iframe or new page
                await page.fill("input[name='site_name']", "My Outreach Site")
                await page.fill("input[name='admin_username']", "admin")
                # Generate a random password for admin or use a default
                admin_pass = "OutreachAgent2026!"
                await page.fill("input[name='admin_pass']", admin_pass)
                
                # Submit
                await page.click("#softsubmit")
                
                # Wait for completion (can take a bit)
                await page.wait_for_selector("text=Congratulations, the software was installed successfully", timeout=60000)
                
                await browser.close()
                return {
                    "status": "success",
                    "admin_user": "admin",
                    "admin_pass": admin_pass,
                    "url": f"http://{domain}"
                }

            except Exception as e:
                await browser.close()
                return {"error": f"cPanel automation failed: {str(e)}"}

    def think(self, context):
        """
        Standard agent interface for reasoning.
        """
        prompt = (
            f"You are a WordPress Expert. Context: {context}\n"
            "Based on the request, suggest the best action and provide technical guidance."
            "If requested to generate a setup, refer to the docker-compose method or cPanel automation."
            "If requested to manage content, explain the REST API approach."
            "Mention that you can now automate cPanel installations and Application Password retrieval."
        )
        return self.provider.generate_text(prompt)
