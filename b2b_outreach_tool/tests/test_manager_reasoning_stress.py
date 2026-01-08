import sys
import os
import unittest
from unittest.mock import MagicMock

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from agents.manager import ManagerAgent

class TestManagerReasoningStress(unittest.TestCase):
    def setUp(self):
        self.manager = ManagerAgent()
        self.manager.provider = MagicMock()

    def test_scenario_b2b_scaling(self):
        """Scenario: Scale B2B agency - should trigger conductor."""
        self.manager.provider.generate_json.return_value = {
            "tool": "conductor_mission",
            "params": {"goal": "Scale B2B agency via lead gen and email", "icp": "IT companies"},
            "reply": "Plan: I'll orchestrate the search and copy agents."
        }
        res = self.manager.think("I want to scale my B2B agency. Find target leads and set up an email sequence.")
        self.assertEqual(res['tool'], "conductor_mission")

    def test_scenario_viral_campaign(self):
        """Scenario: Viral campaign - should trigger conductor."""
        self.manager.provider.generate_json.return_value = {
            "tool": "conductor_mission",
            "params": {"goal": "Viral campaign for AI tool", "icp": "Influencers"},
            "reply": "Plan: Orchestrating influencer search and ad copy."
        }
        res = self.manager.think("Create a viral campaign for our new AI tool. Find influencers and write ad copy.")
        self.assertEqual(res['tool'], "conductor_mission")

    def test_scenario_seo_optimization(self):
        """Scenario: SEO optimization - should trigger conductor."""
        self.manager.provider.generate_json.return_value = {
            "tool": "conductor_mission",
            "params": {"goal": "SEO Optimization", "icp": "High ranking keywords"},
            "reply": "Plan: Keywords and link building orchestration."
        }
        res = self.manager.think("Optimize our SEO. Research keywords and build a link wheel.")
        self.assertEqual(res['tool'], "conductor_mission")

    def test_prompt_contains_all_specialists(self):
        """Check if the prompt contains the key specialists from the registry."""
        self.manager.provider.generate_json.return_value = {"tool": "chat", "reply": "ok"}
        self.manager.think("Help")
        
        args, _ = self.manager.provider.generate_json.call_args
        prompt = args[0]
        
        specialists = ["RESEARCHER", "COPYWRITER", "QUALIFIER", "SEO", "VIDEO", "IMAGE", "PRODUCT_MANAGER"]
        for s in specialists:
            with self.subTest(specialist=s):
                self.assertIn(s, prompt)

if __name__ == '__main__':
    unittest.main()
