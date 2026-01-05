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
