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
    def __init__(self, wp_agent=None, researcher=None, copywriter=None, designer=None):
        self.wp_agent = wp_agent if wp_agent else WordPressAgent()
        self.researcher = researcher if researcher else ResearcherAgent()
        self.copywriter = copywriter if copywriter else CopywriterAgent()
        self.designer = designer if designer else GraphicsDesignerAgent()

    async def run_pipeline(self, site_url, username, app_password, niche, location):
        logger.info(f"--- Starting Autonomous Content Pipeline for {site_url} ---")
        
        # 1. Research Phase
        logger.info(f"🕵️ RESEARCHER: Looking for high-intent keywords for {niche} in {location}...")
        research_context = f"Find high-traffic, low-competition blog post topics for a {niche} business in {location}. Focus on questions customers ask."
        # We use a simple think() here to get a list of topics via LLM reasoning or search
        research_result = self.researcher.think(research_context)
        
        # Pick the best topic (Simulated extraction for now, ideally Researcher returns JSON)
        # Let's ask the Copywriter to parse the Researcher's notes and pick one topic
        topic_selection_prompt = f"From the following research notes, pick ONE best blog post topic:\n\n{research_result}\n\nReturn JUST the topic title."
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
