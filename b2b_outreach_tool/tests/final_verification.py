import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from image_gen import ImageGenManager
from agents import CopywriterAgent, ImageGenAgent
from llm.router import SmartRouter

class TestNewFeatures(unittest.TestCase):

    @patch('image_gen.openai_provider.OpenAI')
    @patch('config.config')
    def test_image_gen_manager(self, mock_config, mock_openai):
        # Test Default Loading
        mock_config.get.return_value = {'default_provider': 'openai'}
        manager = ImageGenManager()
        self.assertIn('openai', manager.providers)
        
    @patch('config.config')
    def test_performance_mode_router(self, mock_config):
        # Mock providers
        p1 = MagicMock()
        p1.model = ':free_model'
        p1.__class__.__name__ = 'OpenRouterProvider'
        
        p2 = MagicMock()
        p2.model = 'gpt-4'
        p2.__class__.__name__ = 'OpenAIProvider'
        
        router = SmartRouter([p1, p2])
        
        # Test FREE mode
        # config.get('project', {}).get('performance_mode')
        mock_config.get.side_effect = lambda k, d=None: {'performance_mode': 'free'} if k == 'project' else {}
        
        # Reset blacklist
        router._blacklist = {}
        
        providers = router._get_providers_for_request()
        # Should only have p1 (free)
        self.assertEqual(len(providers), 1)
        self.assertEqual(providers[0], p1)
        
        # Test PAID mode
        mock_config.get.side_effect = lambda k, d=None: {'performance_mode': 'paid'} if k == 'project' else {}
        
        # Reset blacklist
        router._blacklist = {}
        
        providers = router._get_providers_for_request()
        # Should have both
        self.assertEqual(len(providers), 2)

    @patch('config.config')
    def test_personalization_levels(self, mock_config):
        agent = CopywriterAgent()
        agent.provider = MagicMock() # Mock LLM
        
        # Test GENERIC
        mock_config.get.side_effect = lambda k, d=None: {'personalization': 'generic'} if k == 'campaign' else {}
        
        agent.think("test lead")
        call_args = agent.provider.generate_json.call_args[0][0]
        self.assertIn("standard value proposition", call_args)
        self.assertIn("Generic mode active", call_args)

        # Test HYPER
        mock_config.get.side_effect = lambda k, d=None: {'personalization': 'hyper'} if k == 'campaign' else {}
        
        agent.think("test lead")
        call_args = agent.provider.generate_json.call_args[0][0]
        self.assertIn("highly personalized", call_args)

if __name__ == '__main__':
    unittest.main()
