
import unittest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# MOCK HEAVY MODULES BEFORE IMPORT
sys.modules['services.rag_service'] = MagicMock()
sys.modules['services.rag_service'].rag_service = MagicMock()
sys.modules['lollms'] = MagicMock()
sys.modules['lollms.client'] = MagicMock()

from agents.influencer_agent import InfluencerAgent

class TestInfluencerSearchLogic(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # We patch the provider to avoid actual LLM calls during init if any
        self.mock_provider = MagicMock()
        self.agent = InfluencerAgent(provider=self.mock_provider)
        
        # Mock methods that interact with external world
        self.agent.mass_harvest = AsyncMock()
        self.agent.fetch_html = AsyncMock(return_value="<html>Mock Profile</html>")
        # Mocking save_work to avoid DB writes during test
        self.agent.save_work = MagicMock()

    async def test_iterative_search_flow(self):
        """
        Verifies that scout_influencers iterates through tiers until limit is reached.
        """
        print("\nTesting Iterative Search Logic with REAL InfluencerAgent...")

        # Setup Mock Side Effects for mass_harvest
        # We want to simulate:
        # Tier 1 calls -> Return []
        # Tier 2 calls -> Return [Some Results]
        
        async def mock_harvest_side_effect(term, num_results=50):
            # If the term looks like a Tier 1 term (business inquiries)
            if "business inquiries" in term:
                return []
            # If the term looks like a Tier 2 term (follower)
            elif "follower" in term:
                # Return 5 fake results
                return [
                    {'url': f'https://instagram.com/user_{i}', 'title': f'User {i}', 'snippet': 'Snippet'}
                    for i in range(5)
                ]
            return []

        self.agent.mass_harvest.side_effect = mock_harvest_side_effect
        
        # Execute
        # Request limit=3. Tier 1 should fail, Tier 2 should provide 5, we should stop after 3.
        results = await self.agent.scout_influencers("fitness", "instagram", limit=3)

        # Assertions
        print(f"Total Results: {len(results)}")
        self.assertEqual(len(results), 3, "Should have collected exactly 3 influencers")
        
        # Verify Tier 1 was attempted
        tier_1_called = any("business inquiries" in args[0] for args in self.agent.mass_harvest.call_args_list)
        self.assertTrue(tier_1_called, "Should have attempted Tier 1 search terms")
        
        # Verify Tier 2 was attempted
        tier_2_called = any("follower" in args[0] for args in self.agent.mass_harvest.call_args_list)
        self.assertTrue(tier_2_called, "Should have attempted Tier 2 search terms")

        print("SUCCESS: Search limit respected and tiers traversed using actual Agent logic.")

if __name__ == "__main__":
    unittest.main()
