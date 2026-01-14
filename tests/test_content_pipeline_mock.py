import unittest
from unittest.mock import MagicMock, AsyncMock
import asyncio
import sys
import os

# Add project root to path (parent of tests)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from src.automation_routines.content_pipeline import ContentPipeline

class TestContentPipeline(unittest.TestCase):
    def setUp(self):
        self.mock_wp = AsyncMock()
        self.mock_researcher = MagicMock() # think is sync
        self.mock_copywriter = MagicMock()
        self.mock_designer = MagicMock()
        
        # Setup specific returns
        self.mock_researcher.think.return_value = "Top 5 Roofing Tips"
        
        # Copywriter provider mock for text generation
        self.mock_copywriter.provider = MagicMock()
        self.mock_copywriter.provider.generate_text.return_value = "Roofing Maintenance 101"
        
        # Copywriter generate_seo_article
        self.mock_copywriter.generate_seo_article.return_value = {
            "title": "Roofing Maintenance 101",
            "body_markdown": "## Intro\nFix your roof."
        }
        
        # Designer
        self.mock_designer.think.return_value = {
            "local_path": "fake_image.png"
        }
        
        # WP Agent
        self.mock_wp.manage_content.side_effect = [
            {"id": 123}, # Upload media response
            {"id": 456, "link": "http://example.com/post"} # Create post response
        ]

        self.pipeline = ContentPipeline(
            wp_agent=self.mock_wp,
            researcher=self.mock_researcher,
            copywriter=self.mock_copywriter,
            designer=self.mock_designer
        )

    def test_run_pipeline(self):
        async def run_test():
            # Create fake image file for existence check
            with open("fake_image.png", "w") as f:
                f.write("fake")
                
            await self.pipeline.run_pipeline(
                "http://test.com", "user", "pass", "Roofing", "Austin"
            )
            
            # Verify calls
            self.mock_researcher.think.assert_called()
            self.mock_copywriter.generate_seo_article.assert_called()
            self.mock_designer.think.assert_called()
            
            # Verify WP calls
            # 1. Upload
            self.mock_wp.manage_content.assert_any_call(
                site_url="http://test.com",
                username="user",
                app_password="pass",
                action="upload_media",
                data={"file_path": "fake_image.png"}
            )
            
            # 2. Post
            self.mock_wp.manage_content.assert_called_with(
                site_url="http://test.com",
                username="user",
                app_password="pass",
                action="create_post",
                data={
                    "title": "Roofing Maintenance 101",
                    "content": "## Intro\nFix your roof.",
                    "status": "draft",
                    "featured_media": 123
                }
            )

        # Run async test
        asyncio.run(run_test())
        
        # Cleanup
        if os.path.exists("fake_image.png"):
            os.remove("fake_image.png")

if __name__ == "__main__":
    unittest.main()
