import sys
import os
import unittest
from unittest.mock import MagicMock

# Appends src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from agents.base import BaseAgent

class TestAgentRobustness(unittest.TestCase):
    def setUp(self):
        self.mock_provider = MagicMock()
        self.agent = BaseAgent(role="Test Agent", goal="Testing robustness", provider=self.mock_provider)

    def test_json_dict_return_dict(self):
        # Case: Returns dict, Expect dict
        self.mock_provider.generate_json.return_value = {"key": "value"}
        res = self.agent.generate_json("any prompt")
        self.assertEqual(res, {"key": "value"})

    def test_json_list_return_dict(self):
        # Case: Returns [dict], Expect dict
        self.mock_provider.generate_json.return_value = [{"key": "value"}]
        res = self.agent.generate_json("any prompt")
        self.assertEqual(res, {"key": "value"})

    def test_json_empty_list_return_dict(self):
        # Case: Returns [], Expect dict
        self.mock_provider.generate_json.return_value = []
        res = self.agent.generate_json("any prompt")
        self.assertEqual(res, {})

    def test_json_dict_return_list(self):
        # Case: Returns dict, Expect list
        self.mock_provider.generate_json.return_value = {"key": "value"}
        res = self.agent.generate_json("any prompt", expect_list=True)
        self.assertEqual(res, [{"key": "value"}])

    def test_json_list_return_list(self):
        # Case: Returns list, Expect list
        self.mock_provider.generate_json.return_value = [{"key": "value"}]
        res = self.agent.generate_json("any prompt", expect_list=True)
        self.assertEqual(res, [{"key": "value"}])

if __name__ == "__main__":
    unittest.main()
