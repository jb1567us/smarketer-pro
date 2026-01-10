import sys
import os
import unittest
from unittest.mock import MagicMock

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from agents.manager import ManagerAgent
from memory import Memory

class TestProactivityAndLearning(unittest.TestCase):
    def setUp(self):
        self.memory = Memory()
        # Reset memory for test
        self.memory.data = {"preferences": [], "feedback": [], "history": [], "insights": [], "style": {}}
        self.manager = ManagerAgent()
        self.manager.memory = self.memory

    def test_learning_and_recall(self):
        """Verifies manager can save an insight and recall it in prompt."""
        # 1. Simulate manager deciding to learn something
        insight = "User likes to focus on high-ticket SaaS leads only."
        self.memory.add_insight(insight)
        
        # 2. Check if the insight is in the prompt for the NEXT thought
        self.manager.provider = MagicMock()
        self.manager.provider.generate_json.return_value = {"tool": "chat", "reply": "Understood"}
        
        self.manager.think("Find some leads for me")
        
        args, _ = self.manager.provider.generate_json.call_args
        prompt = args[0]
        
        self.assertIn("LEARNED INSIGHTS & PATTERNS", prompt)
        self.assertIn(insight, prompt)

    def test_proactive_suggestion_structure(self):
        """Checks if the system prompt includes proactivity instructions."""
        self.manager.provider = MagicMock()
        self.manager.provider.generate_json.return_value = {"tool": "chat", "reply": "Understood"}
        
        self.manager.think("Hello")
        
        args, _ = self.manager.provider.generate_json.call_args
        prompt = args[0]
        
        self.assertIn("CRITICAL: Be proactive and contemplative", prompt)
        self.assertIn("SUGGEST: Proactively suggest tools or workflows", prompt)

if __name__ == '__main__':
    unittest.main()
