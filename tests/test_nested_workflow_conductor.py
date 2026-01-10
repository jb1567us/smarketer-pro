import asyncio
import sys
import os
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import json

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from automation_engine import AutomationEngine
from agents.manager import ManagerAgent
from workflow_manager import save_workflow, delete_workflow

class TestNestedWorkflowConductor(unittest.TestCase):
    def setUp(self):
        # Create a dummy workflow
        self.wf_name = "test_nested_1.md"
        self.steps = [
            {"tool": "run_search", "params": {"query": "nested query", "limit": 1}}
        ]
        save_workflow(self.wf_name, "Test Content", "Test Description", steps=self.steps)

    def tearDown(self):
        delete_workflow(self.wf_name)

    def test_manager_sees_workflow(self):
        """Verifies Manager counts the new workflow in its prompt."""
        manager = ManagerAgent()
        manager.provider = MagicMock()
        manager.provider.generate_json.return_value = {"tool": "chat", "reply": "ok"}
        
        manager.think("list workflows")
        
        args, _ = manager.provider.generate_json.call_args
        prompt = args[0]
        self.assertIn(self.wf_name, prompt)

    def test_conductor_executes_workflow_sequence(self):
        """Verifies AutomationEngine executes a sequence with a workflow."""
        async def run_test():
            engine = AutomationEngine()
            mock_manager = MagicMock(spec=ManagerAgent)
            mock_manager.run_mission = AsyncMock(return_value={"status": "complete", "leads": []})
            
            strategy = {
                "goal": "Run nested workflow",
                "mode": "conductor",
                "sequence": [
                    {"type": "workflow", "name": self.wf_name}
                ]
            }
            
            engine._is_running = True
            await engine._execute_mission_logic(strategy, mock_manager)
            
            log_text = "\n".join(engine.logs)
            print(log_text)
            
            self.assertIn(f"Executing Nested Workflow: {self.wf_name}", log_text)
            self.assertIn("Workflow 'test_nested_1.md' completed", log_text)
            
            # Verify manager.run_mission was called for the nested step
            mock_manager.run_mission.assert_called()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_test())
        loop.close()

if __name__ == '__main__':
    unittest.main()
