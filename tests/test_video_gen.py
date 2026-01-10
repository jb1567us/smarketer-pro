import unittest
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from video_gen.manager import VideoGenManager
from video_gen.mock import MockProvider
from agents.video_agent import VideoAgent

class TestVideoGen(unittest.TestCase):
    def test_manager_defaults(self):
        manager = VideoGenManager()
        provider = manager.get_provider()
        self.assertIsInstance(provider, MockProvider)
        self.assertEqual(manager.default_provider, "mock")

    def test_mock_generation(self):
        manager = VideoGenManager()
        provider = manager.get_provider("mock")
        
        result = provider.generate_video("Test prompt")
        self.assertEqual(result['status'], "processing")
        self.assertIsNotNone(result.get('job_id'))
        
        # Check status
        status = provider.get_status(result['job_id'])
        self.assertIn(status['status'], ["processing", "completed"])

    def test_video_agent(self):
        agent = VideoAgent()
        # Mock the prompt method since we don't want to call actual LLM in unit test
        agent.prompt = lambda context, instructions: "Optimized Prompt: " + context
        
        res = agent.create_video("A flying car", provider_name="mock")
        self.assertEqual(res['provider'], "mock")
        self.assertIn("Optimized Prompt", res['optimized_prompt'])
        self.assertIsNotNone(res['job']['job_id'])

    def test_provider_imports(self):
        """
        Verify that real provider modules can be imported without error.
        """
        try:
            from video_gen.luma import LumaProvider
            from video_gen.stability import StabilityProvider
            from video_gen.openai_video import OpenAIVideoProvider
        except ImportError as e:
            self.fail(f"Failed to import real providers: {e}")


if __name__ == '__main__':
    unittest.main()

class TestSmartRouterLogic(unittest.TestCase):
    def setUp(self):
        from video_gen.manager import VideoGenManager
        self.manager = VideoGenManager()

    def test_smart_routing_logic(self):
        # 1. Verify Browser Providers exist
        providers = self.manager.list_providers()
        self.assertIn("smart", providers)
        
        # 2. Test Routing
        # Reset Mock Usage
        self.manager.usage_stats = {}
        
        # Test: Cinematic -> Prefer Luma (if default logic holds and tags match)
        # Note: We rely on the hardcoded capabilities in browser_providers.py
        p = self.manager.smart_route("test prompt", "Cinematic")
        self.assertTrue(hasattr(p, 'name'))
        print(f"Selected Provider for Cinematic: {p.name}")

    def test_limits_logic(self):
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Mock Luma as full
        self.manager.usage_stats["luma"] = {today: 999}
        
        p = self.manager.smart_route("test prompt", "Cinematic")
        # Should NOT be luma
        self.assertNotEqual(p.name, "luma", "Should fallback if over limit")
