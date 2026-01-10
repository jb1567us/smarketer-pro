import sys
import os
import unittest
from unittest.mock import MagicMock

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from agents.manager import ManagerAgent

class TestManagerSchemaEnforcement(unittest.TestCase):
    def setUp(self):
        self.manager = ManagerAgent()
        self.manager.provider = MagicMock()

    def test_prompt_contains_strict_json_schema(self):
        """Check if the prompt contains the strict JSON schema instructions."""
        # Mock response to avoid actual LLM call failure (though logic shouldn't reach parsing if we just check prompt)
        self.manager.provider.generate_json.return_value = {"tool": "chat", "reply": "ok"}
        
        self.manager.think("test input")
        
        args, _ = self.manager.provider.generate_json.call_args
        prompt = args[0]
        
        # Strings that MUST be in the prompt now
        required_schema_strings = [
            "CRITICAL RESPONSE FORMAT:",
            "You MUST return valid JSON matching this schema exactly:",
            "\"tool\": \"string",
            "\"params\": {",
            "\"reply\": \"string",
            "Do not return markdown blocks or plain text. JUST the JSON."
        ]
        
        for s in required_schema_strings:
            with self.subTest(schema_string=s):
                self.assertIn(s, prompt)

if __name__ == '__main__':
    unittest.main()
