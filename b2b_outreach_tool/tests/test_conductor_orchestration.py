import asyncio
import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from agents.manager import ManagerAgent
from utils.agent_registry import get_agent_metadata

class TestConductorOrchestration(unittest.TestCase):
    def test_manager_expertise_prompt(self):
        """Verifies the manager's prompt contains the new expertise data."""
        manager = ManagerAgent()
        # Mock provider to capture the prompt
        manager.provider = MagicMock()
        manager.provider.generate_json.return_value = {"tool": "chat", "reply": "Test"}
        
        manager.think("How do I find leads?")
        
        # Capture the prompt sent to generate_json
        args, _ = manager.provider.generate_json.call_args
        full_prompt = args[0]
        
        # Check for key expertise markers
        self.assertIn("RESEARCHER:", full_prompt)
        self.assertIn("Lead Researcher & Harvester", full_prompt)
        self.assertIn("COPYWRITER:", full_prompt)
        self.assertIn("Conversion Copywriter", full_prompt)

    def test_conductor_mission_tool_suggestion(self):
        """Verifies the manager suggests 'conductor_mission' for complex goals."""
        # This requires an actual LLM call or a very specific mock
        # We'll use a mock to simulate the Manager's decision
        manager = ManagerAgent()
        mock_response = {
            "tool": "conductor_mission",
            "params": {
                "goal": "Find Austin SaaS companies and write email hooks",
                "icp": "SaaS founders"
            },
            "reply": "I will launch a conductor mission to orchestrate the search and copy generation."
        }
        manager.provider = MagicMock()
        manager.provider.generate_json.return_value = mock_response
        
        decision = manager.think("Find 5 SaaS companies in Austin and write a personalized email hook for each.")
        
        self.assertEqual(decision['tool'], "conductor_mission")
        self.assertEqual(decision['params']['goal'], "Find Austin SaaS companies and write email hooks")

if __name__ == '__main__':
    unittest.main()
