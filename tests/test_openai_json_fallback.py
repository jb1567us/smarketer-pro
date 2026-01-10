import unittest
from unittest.mock import MagicMock, patch
import requests
import json
import sys
import os

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from llm.openai_compatible import OpenAICompatibleProvider

class TestOpenAIJsonFallback(unittest.TestCase):
    def setUp(self):
        self.provider = OpenAICompatibleProvider("fake_key", "http://fake.url", "fake_model")

    @patch('requests.post')
    def test_generate_json_fallback_success(self, mock_post):
        # Setup mock for first call (400 Bad Request)
        mock_response_400 = MagicMock()
        mock_response_400.status_code = 400
        mock_response_400.raise_for_status.side_effect = requests.exceptions.HTTPError("400 Client Error", response=mock_response_400)
        
        # Setup mock for second call (fallback text generation)
        mock_response_200 = MagicMock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = {
            "choices": [{"message": {"content": '{"test": "success"}'}}]
        }
        
        # Configure side effects: 
        # 1-3 tries for first call (retry logic in _call_api), we want it to fail once with 400
        # Wait, _call_api has internal retries. HTTPError usually raised after 1 attempt if we configure it right or mocks need to handle it.
        # Actually, `_call_api` loops 3 times. If we want to simulate the result of `_call_api` throwing an exception, we should patch `_call_api` directly? 
        # But we modified `generate_json` which calls `_call_api`.
        # Let's mock `_call_api` for easier testing of logic flow in `generate_json`.
        pass

    @patch.object(OpenAICompatibleProvider, '_call_api')
    @patch.object(OpenAICompatibleProvider, 'generate_text')
    def test_fallback_logic(self, mock_generate_text, mock_call_api):
        # Scenario: First call raises HTTPError 400
        mock_resp_400 = MagicMock()
        mock_resp_400.status_code = 400
        error = requests.exceptions.HTTPError("400 Bad Request", response=mock_resp_400)
        
        mock_call_api.side_effect = error
        
        # Fallback text generation returns valid string
        mock_generate_text.return_value = '{"fallback": "works"}'

        # Execute
        result = self.provider.generate_json("test prompt")
        
        # Assertions
        # 1. Verify first call used json_object
        mock_call_api.assert_called_with([{"role": "user", "content": "test prompt"}], response_format={"type": "json_object"})
        
        # 2. Verify fallback called generate_text
        mock_generate_text.assert_called_once()
        args, _ = mock_generate_text.call_args
        self.assertIn("CRITICAL: Return valid JSON only", args[0])
        
        # 3. Verify result parsed correctly
        self.assertEqual(result, {"fallback": "works"})

    @patch.object(OpenAICompatibleProvider, '_call_api')
    def test_non_400_error_reraised(self, mock_call_api):
        # Scenario: 401 Unauthorized should NOT trigger fallback
        mock_resp_401 = MagicMock()
        mock_resp_401.status_code = 401
        error = requests.exceptions.HTTPError("401 Unauthorized", response=mock_resp_401)
        
        mock_call_api.side_effect = error
        
        with self.assertRaises(requests.exceptions.HTTPError):
            self.provider.generate_json("test")

if __name__ == '__main__':
    unittest.main()
