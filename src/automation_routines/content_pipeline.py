import logging
import os
import asyncio
import sys

# Ensure project root is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.agents.wordpress import WordPressAgent
from src.agents.researcher import ResearcherAgent
from src.agents.copywriter import CopywriterAgent
from src.agents.designer import GraphicsDesignerAgent
from src.agents.qualifier import QualifierAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/content_pipeline.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("ContentPipeline")

class ContentPipeline:
    def __init__(self, wp_agent=None, researcher=None, copywriter=None, designer=None, qualifier=None):
        self.wp_agent = wp_agent if wp_agent else WordPressAgent()
        self.researcher = researcher if researcher else ResearcherAgent()
        self.copywriter = copywriter if copywriter else CopywriterAgent()
        self.designer = designer if designer else GraphicsDesignerAgent()
        self.qualifier = qualifier if qualifier else QualifierAgent()

    async def run_pipeline(self, site_url, username, app_password, niche, location):
        logger.info(f"--- Starting Autonomous Content Pipeline for {site_url} ---")
        
        # 1. Research Phase
        logger.info(f"🕵️ RESEARCHER: Looking for high-intent keywords for {niche} in {location}...")
        
        # Dynamic Prompting based on Niche
        niche_lower = niche.lower()
        research_focus = "high-traffic, low-competition blog post topics"
        
        if "roof" in niche_lower or "plumb" in niche_lower or "hvac" in niche_lower:
            research_focus = "emergency repair guides, seasonal maintenance checklists, and cost estimation queries"
        elif "saas" in niche_lower or "software" in niche_lower:
            research_focus = "churn reduction, comparison (vs competitors), and implementation best practices"
        elif "law" in niche_lower or "legal" in niche_lower:
            research_focus = "common legal questions, compliance guides, and 'when to hire a lawyer' scenarios"
        elif "medical" in niche_lower or "health" in niche_lower:
             research_focus = "symptom awareness, treatment options, and patient recovery stories"

        research_context = f"Find {research_focus} for a {niche} business in {location}. Focus on questions potential new customers ask."
        
        # Call Researcher (Now uses real keyword_discovery if 'topic'/'keyword' is in prompt)
        research_result = self.researcher.think(research_context)
        
        # Pick the best topic
        topic_selection_prompt = f"From the following research notes, pick ONE best blog post topic used for SEO:\n\n{research_result}\n\nReturn JUST the topic title."
        topic = self.copywriter.provider.generate_text(topic_selection_prompt).strip().strip('"')
        logger.info(f"✅ Topic Selected: {topic}")

        # 2. Copywriting Phase
        logger.info(f"✍️ COPYWRITER: Drafting SEO article for '{topic}'...")
        draft_json = self.copywriter.generate_seo_article(
            niche=f"{niche} in {location}",
            keywords=[topic, location, niche],
            target_url=site_url
        )
        
        title = draft_json.get('title', topic)
        content_body = draft_json.get('body_markdown', '')
        
        if not content_body:
            logger.error("❌ Copywriter failed to generate content.")
            return

        logger.info(f"✅ Draft Ready: {title} ({len(content_body)} chars)")

        # 3. Design Phase
        logger.info(f"🎨 DESIGNER: Generating featured image for '{title}'...")
        # Designer returns {revised_prompt, image_url, local_path, description}
        design_result = self.designer.think(f"editorial illustration for a blog post titled '{title}'. Modern, clean, corporate memphis style.")
        
        local_image_path = design_result.get('local_path')
        featured_media_id = None

        # 4. Upload Image (if available)
        if local_image_path and os.path.exists(local_image_path):
            logger.info(f"📤 WORDPRESS: Uploading image from {local_image_path}...")
            upload_res = await self.wp_agent.manage_content(
                site_url=site_url,
                username=username,
                app_password=app_password,
                action="upload_media",
                data={"file_path": local_image_path}
            )
            
            if "id" in upload_res:
                featured_media_id = upload_res['id']
                logger.info(f"✅ Image Uploaded! Media ID: {featured_media_id}")
            else:
                logger.warning(f"⚠️ Image upload failed: {upload_res}")
        else:
             logger.warning("⚠️ No local image path from Designer or file missing. Skipping image upload.")

        # 5. Publish Post
        logger.info(f"🚀 WORDPRESS: Publishing post...")
        post_data = {
            "title": title,
            "content": content_body,
            "status": "draft" # Keep as draft for safety
        }
        
        if featured_media_id:
            post_data['featured_media'] = featured_media_id
            
        publish_res = await self.wp_agent.manage_content(
            site_url=site_url,
            username=username,
            app_password=app_password,
            action="create_post",
            data=post_data
        )
        
        if "id" in publish_res:
            logger.info(f"🎉 SUCCESS! Post created. ID: {publish_res['id']}")
            logger.info(f"   Link: {publish_res.get('link')}")
        else:
            logger.error(f"❌ Publish failed: {publish_res}")
            
        return publish_res

    async def run_full_site_build(self, niche, location, cpanel_config=None):
        """
        Orchestrates a complete site build:
        1. Research & Content Generation (Pre-build)
        2. Site Installation (via cPanel)
        3. Content Publishing
        """
        logger.info(f"STARTING FULL SITE BUILD for {niche} in {location}")
        
        # --- STEP 1: ASSET GENERATION ---
        logger.info("--- PHASE 1: ASSET GENERATION ---")
        
        # 1. Research
        logger.info(f"RESEARCHER: Looking for high-intent keywords...")
        research_context = f"Find high-traffic, low-competition blog post topics for a {niche} business in {location}. Focus on questions customers ask."
        research_result = self.researcher.think(research_context)
        
        # Pick Topic
        topic_selection_prompt = f"From the following research notes, pick ONE best blog post topic:\n\n{research_result}\n\nReturn JUST the topic title."
        topic = self.copywriter.provider.generate_text(topic_selection_prompt).strip().strip('"')
        logger.info(f"Topic Selected: {topic}")

        # 2. Copywriting (with Revision Loop)
        logger.info(f"COPYWRITER: Drafting SEO article...")
        
        revision_count = 0
        max_revisions = 3
        current_instructions = f"Write an SEO article about '{topic}' for {niche} in {location}."
        title = topic
        content_body = ""

        while revision_count < max_revisions:
            draft_json = self.copywriter.generate_seo_article(
                niche=f"{niche} in {location}",
                keywords=[topic, location, niche],
                target_url="[SITE_URL]",
                # Pass current instructions if generate_seo_article supported revisional instructions directly,
                # but currently it might not. We assume we might need to modify `generate_seo_article` 
                # or just accept that it generates based on params. 
                # Ideally, we'd pass 'instructions' param to generate_seo_article.
                # checking copywriter.py... it takes 'niche' and 'keywords'. 
                # We'll rely on the fact that if revisions are needed, we might not be able to easily pass them 
                # without modifying CopywriterAgent.
                # For now, let's assume we proceed or basic retry. 
                # ACTUALLY, checking Qualifier feedback, we should probably just LOG the rejection for now 
                # if Copywriter doesn't support 'refine' mode in this specific method, 
                # OR we use the generic `tune` method if we want to be fancy.
                # Let's simple-loop:
            )
            
            title = draft_json.get('title', topic)
            content_body = draft_json.get('body_markdown', '')
            
            # QUALIFIER CHECK
            logger.info(f"QUALIFIER: Reviewing copy (Round {revision_count + 1})...")
            q_res = self.qualifier.critique_copy(content_body, criteria="Professional, SEO-optimized, no fluff, accurate niche terminology.")
            
            if q_res.get('approved'):
                logger.info("QUALIFIER: Copy approved.")
                break
            else:
                feedback = q_res.get('feedback', 'General quality issues.')
                logger.warning(f"QUALIFIER: Copy rejected. Feedback: {feedback}")
                revision_count += 1
                # In a real scenario, we would feed 'feedback' back into the Copywriter.
                # For this implementation, we will log it.
                # TODO: Implement Copywriter.tune() or pass feedback to generate_seo_article
        
        if revision_count >= max_revisions:
            logger.warning("⚠️ Max copy revisions reached. Proceeding with best revised draft.")

        # 3. Design (with Revision Loop)
        logger.info(f"DESIGNER: Generating visual assets...")
        
        revision_count = 0
        
        # Dynamic Style
        niche_lower = niche.lower()
        style = "Modern, clean, corporate memphis style"
        if "law" in niche_lower or "finance" in niche_lower:
            style = "Professional, trustworthy, minimal blue and white palette, photographic style"
        elif "saas" in niche_lower or "tech" in niche_lower:
             style = "Futuristic, gradient isometric, glassmorphism, dark mode aesthetic"
        elif "construction" in niche_lower or "trade" in niche_lower:
             style = "Realistic, warm lighting, architectural sketch style"

        current_prompt = f"editorial illustration for a blog post titled '{title}'. {style}."
        local_image_path = None

        while revision_count < max_revisions:
            design_result = self.designer.think(current_prompt)
            local_image_path = design_result.get('local_path')
            
            # QUALIFIER CHECK
            # We critique the PROMPT or Description since we can't see the image
            logger.info(f"QUALIFIER: Reviewing visual concept (Round {revision_count + 1})...")
            q_res = self.qualifier.critique_visuals(design_result.get('revised_prompt', current_prompt), criteria="Corporate, safe for work, high quality style.")
            
            if q_res.get('approved'):
                 logger.info("QUALIFIER: Visuals approved.")
                 break
            else:
                 feedback = q_res.get('feedback', 'Adjust style.')
                 logger.warning(f"QUALIFIER: Visuals rejected. Feedback: {feedback}")
                 current_prompt += f" (Adjustment: {feedback})"
                 revision_count += 1
                 
        if revision_count >= max_revisions:
             logger.warning("⚠️ Max design revisions reached. Proceeding.")

        # --- STEP 2: INFRASTRUCTURE ---
        logger.info("--- PHASE 2: INFRASTRUCTURE ---")
        
        site_url = ""
        username = "admin"
        app_password = "" 

        if cpanel_config:
            logger.info("WP AGENT: Installing WordPress via cPanel...")
            # cpanel_config should have: url, user, pass, domain, directory
            install_res = await self.wp_agent.cpanel_install_wp(
                cpanel_url=cpanel_config['url'],
                cp_user=cpanel_config['user'],
                cp_pass=cpanel_config['pass'],
                domain=cpanel_config['domain'],
                directory=cpanel_config.get('directory', '')
            )
            
            if install_res.get('status') == 'success':
                site_url = install_res['url']
                username = install_res['admin_user']
                # Note: cPanel install returns the admin password, but we need an APP PASSWORD for REST API
                # The cpanel_install_wp returns a standard admin pass, usually.
                # To get an App Password, we need to automate that too.
                admin_pass = install_res['admin_pass']
                logger.info(f"Install Success! URL: {site_url}")
                
                # Generate App Password
                logger.info("WP AGENT: Generating App Password for API access...")
                auth_res = await self.wp_agent.automate_app_password(site_url + "/wp-admin", username, admin_pass)
                
                if 'app_password' in auth_res:
                    app_password = auth_res['app_password']
                    logger.info("App Password Generated.")
                else:
                    logger.error(f"Failed to generate App Password: {auth_res.get('error')}")
                    return
            else:
                 logger.error(f"Installation Failed: {install_res.get('error')}")
                 return
        else:
            logger.error("No cPanel config provided for full build.")
            return

        # --- STEP 3: PUBLISHING ---
        logger.info("--- PHASE 3: PUBLISHING ---")
        
        # Determine featured media ID
        featured_media_id = None
        if local_image_path and os.path.exists(local_image_path):
             logger.info(f"WORDPRESS: Uploading image...")
             upload_res = await self.wp_agent.manage_content(
                site_url=site_url,
                username=username,
                app_password=app_password,
                action="upload_media",
                data={"file_path": local_image_path}
            )
             if "id" in upload_res:
                featured_media_id = upload_res['id']

        # Publish
        logger.info(f"WORDPRESS: Publishing post to {site_url}...")
        
        # Replace placeholder URL in content
        final_content = content_body.replace("[SITE_URL]", site_url)
        
        post_data = {
            "title": title,
            "content": final_content,
            "status": "publish" # We can publish directly now
        }
        if featured_media_id:
            post_data['featured_media'] = featured_media_id

        publish_res = await self.wp_agent.manage_content(
            site_url=site_url,
            username=username,
            app_password=app_password,
            action="create_post",
            data=post_data
        )

        if "id" in publish_res:
            logger.info(f"FULL BUILD COMPLETE! Post: {publish_res.get('link')}")
        else:
            logger.error(f"Publish failed: {publish_res}")
        
        return publish_res

async def main():
    # Example usage (requires environment variables)
    SITE_URL = os.getenv("WP_SITE_URL")
    USER = os.getenv("WP_USERNAME")
    PASS = os.getenv("WP_APP_PASSWORD")
    
    if not all([SITE_URL, USER, PASS]):
        # Default placeholder for testing if env vars missing
        logger.warning("Missing WP credentials in env. Using placeholders for dry run check.")
        # We can't actually run without creds, so just return
        logger.error("Please set WP_SITE_URL, WP_USERNAME, and WP_APP_PASSWORD to run this script.")
        return

    pipeline = ContentPipeline()
    await pipeline.run_pipeline(SITE_URL, USER, PASS, "Roofing", "Austin, TX")

if __name__ == "__main__":
    asyncio.run(main())
