import asyncio
import sys
import os
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import time

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from automation_engine import AutomationEngine
from agents.manager import ManagerAgent

class TestConductorLiveFlow(unittest.TestCase):
    def test_conductor_full_logic_flow(self):
        """Verifies the AutomationEngine correctly sequences a Conductor mission."""
        async def run_test():
            engine = AutomationEngine()
            # Mock ManagerAgent
            mock_manager = MagicMock(spec=ManagerAgent)
            
            # Mock run_mission to return a success result with leads
            mock_manager.run_mission = AsyncMock(return_value={
                "status": "complete",
                "leads": [{"url": "http://test.com", "title": "Test Lead"}]
            })
            
            strategy = {
                "strategy_name": "Test Integration Strategy",
                "goal": "Test orchestration",
                "mode": "conductor",
                "queries": ["test search"],
                "limit": 1
            }
            
            # We need to reach inside and run the logic
            engine._is_running = True # Simulate start
            print("Running _execute_mission_logic...")
            
            # Mock time.sleep to avoid waiting
            with patch('time.sleep', return_value=None):
                with patch('utils.agent_registry.get_agent_class') as mock_get_class:
                    # Mock Copywriter
                    mock_copywriter_class = MagicMock()
                    mock_copywriter_instance = MagicMock()
                    mock_copywriter_class.return_value = mock_copywriter_instance
                    mock_get_class.return_value = mock_copywriter_class
                    
                    await engine._execute_mission_logic(strategy, mock_manager)
            
            # Verify logs for phase transitions
            log_text = "\n".join(engine.logs)
            print("Logs generated during test:")
            print(log_text)
            
            self.assertIn("Conductor Mode Active", log_text)
            self.assertIn("Phase 1: Market Intelligence Gathering", log_text)
            self.assertIn("Phase 2: Orchestrating Personalized Copy", log_text)
            self.assertIn("Phase 3: Preparing for Outreach Deployment", log_text)
            self.assertIn("Conductor Mission Phase Complete", log_text)
            
            # Verify Manager was called for research
            mock_manager.run_mission.assert_called_once()
            
            # Verify Copywriter was fetched
            mock_get_class.assert_called_with("copywriter")

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_test())
        loop.close()

if __name__ == '__main__':
    unittest.main()
