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
        self.mock_designer = MagicMock()
        self.mock_qualifier = MagicMock()
        self.mock_expert = MagicMock()
        
        # Setup specific returns
        # Expert return for analyze_niche
        self.mock_expert.analyze_niche.return_value = {
            "icp_role": "Homeowner",
            "icp_pain_points": ["Leak", "Mold"],
            "icp_desires": ["Dry House"],
            "brand_voice": "Reliable"
        }
        # The new logic executes keyword discovery and returns a formatted string "\n- Topic ..."
        self.mock_researcher.think.return_value = "- Ranked Research Topic: Top 5 Roofing Tips"
        
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
            designer=self.mock_designer,
            qualifier=self.mock_qualifier,
            prompt_expert=self.mock_expert
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

    def test_run_full_site_build(self):
        async def run_build_test():
             # Create fake image
            with open("fake_image_build.png", "w") as f:
                f.write("fake")

            self.mock_designer.think.return_value = {
                "local_path": "fake_image_build.png"
            }
            
            # Mock Installation Returns
            self.mock_wp.cpanel_install_wp.return_value = {
                "status": "success",
                "url": "http://newsite.com",
                "admin_user": "admin",
                "admin_pass": "temp_pass"
            }
            self.mock_wp.automate_app_password.return_value = {
                "app_password": "new_app_pass"
            }
            
            # Qualifier Mocks
            # 1. Copy Review: Approve immediately
            self.mock_qualifier.critique_copy.return_value = {"approved": True}
            
            # 2. Visual Review: Reject once, then Approve
            self.mock_qualifier.critique_visuals.side_effect = [
                {"approved": False, "feedback": "Make it more blue."}, # Round 1
                {"approved": True} # Round 2
            ]

            # Run
            cpanel_conf = {
                "url": "https://cpanel.host.com",
                "user": "cpuser",
                "pass": "cppass",
                "domain": "newsite.com"
            }
            
            await self.pipeline.run_full_site_build(
                "Plumbing", "Dallas", cpanel_config=cpanel_conf
            )
            
            # Verify Flow
            # 1. Asset Gen
            self.mock_researcher.think.assert_called()
            self.mock_designer.think.assert_called()
            # Expect 2 calls to designer (1 initial + 1 revision)
            self.assertEqual(self.mock_designer.think.call_count, 2)
            
            # Verify Kernel Bootstrap
            self.mock_expert.analyze_niche.assert_called_once()
            self.mock_qualifier.set_kernel.assert_called_once()

            # Qualifier Calls
            self.mock_qualifier.critique_copy.assert_called_once()
            self.assertEqual(self.mock_qualifier.critique_visuals.call_count, 2)

            # 2. Install
            self.mock_wp.cpanel_install_wp.assert_called_with(
                cpanel_url="https://cpanel.host.com",
                cp_user="cpuser",
                cp_pass="cppass",
                domain="newsite.com",
                directory=""
            )
            
            # 3. App Pass
            self.mock_wp.automate_app_password.assert_called()
            
            # 4. Publish (to NEW URL)
            self.mock_wp.manage_content.assert_called_with(
                site_url="http://newsite.com",
                username="admin",
                app_password="new_app_pass",
                action="create_post",
                data={
                    "title": "Roofing Maintenance 101",
                    "content": "## Intro\nFix your roof.".replace("[SITE_URL]", "http://newsite.com"),
                    "status": "publish",
                    "featured_media": 123
                }
            )

        asyncio.run(run_build_test())
        
        if os.path.exists("fake_image_build.png"):
            os.remove("fake_image_build.png")

        if os.path.exists("fake_image.png"):
            os.remove("fake_image.png")

if __name__ == "__main__":
    unittest.main()
