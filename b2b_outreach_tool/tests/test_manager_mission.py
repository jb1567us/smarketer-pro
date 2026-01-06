import asyncio
import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from agents.manager import ManagerAgent
import database

class TestManagerMission(unittest.TestCase):
    def test_run_mission_delegation(self):
        async def run_test():
            print("\n--- Starting Manager Mission Test ---")
            # Mock provider for ManagerAgent
            mock_provider = MagicMock()
            manager = ManagerAgent(provider=mock_provider)
            
            # Plan
            plan = {
                "search_queries": ["site:test-mission.com"],
                "limit": 5
            }
            
            # Patch ResearcherAgent where it is DEFINED, which is agents.researcher
            # Since manager.py does `from .researcher import ResearcherAgent`, it uses the class from that module.
            with patch('agents.researcher.ResearcherAgent') as MockResearcher:
                # Configure the mock instance
                mock_researcher_instance = MockResearcher.return_value
                
                # Mock mass_harvest to be an async method returning a list
                async def mock_harvest(*args, **kwargs):
                    return [
                        {"url": "http://test-mission.com/1", "title": "Test 1", "platform": "WordPress"},
                        {"url": "http://test-mission.com/2", "title": "Test 2", "platform": "Drupal"}
                    ]
                
                mock_researcher_instance.mass_harvest.side_effect = mock_harvest
                
                # Run the mission
                print("Executing manager.run_mission()...")
                result = await manager.run_mission("Test Goal", plan_override=plan, status_callback=lambda x: print(f"[Manager] {x}"))
                
                # 1. Verify wrapper behavior
                self.assertEqual(result['status'], 'complete')
                self.assertEqual(len(result['leads']), 2)
                
                # 2. Verify Researcher was called correcty
                mock_researcher_instance.mass_harvest.assert_called_once()
                args, _ = mock_researcher_instance.mass_harvest.call_args
                self.assertEqual(args[0], "site:test-mission.com")

                # 3. Verify DB insertion (Integration check)
                print("Verifying database records...")
                ids = []
                for item in result['leads']:
                    # It might be None if it already existed (duplicate), but in a clean test run it should be int
                    # If it existed, result['id'] might not be set by my logic? 
                    # Let's check my logic: 
                    # lid = add_lead(...)
                    # if lid: res['id'] = lid
                    # collected_leads.append(res)
                    # Ah, if add_lead returns None (duplicate), it still appends the res, but without 'id'.
                    # We should handle this.
                    if item.get('id'):
                        ids.append(item['id'])

                # Verify they are in DB by querying
                conn = database.get_connection()
                c = conn.cursor()
                c.execute("SELECT count(*) FROM leads WHERE url LIKE 'http://test-mission.com%'")
                count = c.fetchone()[0]
                conn.close()
                
                print(f"Leads found in DB: {count}")
                self.assertGreaterEqual(count, 2)
                
                # Cleanup
                if ids:
                    print(f"Cleaning up {len(ids)} test leads...")
                    database.delete_leads(ids)
                
                print("Test passed successfully.")

        # Run async test in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_test())
        loop.close()

if __name__ == '__main__':
    unittest.main()
