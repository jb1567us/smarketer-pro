
import unittest
from unittest.mock import MagicMock
import json
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from agents.manager import ManagerAgent
from utils.recorder import WorkflowRecorder
from workflow_manager import save_workflow, extract_steps_from_workflow, delete_workflow

class TestManagerWorkflow(unittest.TestCase):
    def setUp(self):
        self.mock_provider = MagicMock()
        self.agent = ManagerAgent(provider=self.mock_provider)
        self.recorder = WorkflowRecorder()
        self.test_wf_name = "test_auto_workflow"

    def tearDown(self):
        delete_workflow(self.test_wf_name + ".md")

    def test_manager_think_search(self):
        # Simulate LLM response for a search command
        expected_response = {
            "tool": "run_search",
            "params": {"query": "SaaS Companies", "niche": "Tech"},
            "reply": "Searching for SaaS companies..."
        }
        self.mock_provider.generate_json.return_value = expected_response
        
        response = self.agent.think("Find me SaaS companies")
        self.assertEqual(response['tool'], 'run_search')
        self.assertEqual(response['params']['query'], 'SaaS Companies')

    def test_workflow_recording_and_saving(self):
        # 1. Record some steps
        self.recorder.log_step("run_search", {"query": "foo"}, "Search for foo")
        self.recorder.log_step("qualify_leads", {}, "Qualify")
        
        steps = self.recorder.get_workflow()
        self.assertEqual(len(steps), 2)
        
        # 2. Save workflow
        save_workflow(self.test_wf_name, "Test Description", steps=steps)
        
        # 3. Verify file execution
        loaded_steps = extract_steps_from_workflow(self.test_wf_name + ".md")
        self.assertEqual(len(loaded_steps), 2)
        self.assertEqual(loaded_steps[0]['tool'], 'run_search')

if __name__ == '__main__':
    unittest.main()
