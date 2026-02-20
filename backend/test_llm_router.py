import unittest
import asyncio
from backend.llm_router import SmartRouter, LLMTier, LLMProvider

class TestLLMRouter(unittest.TestCase):
    def setUp(self):
        self.router = SmartRouter()

    def test_tier_selection(self):
        economy_provider = self.router.get_provider(LLMTier.ECONOMY)
        self.assertIn(economy_provider.name, ["Gemini-Flash", "GPT-4o-Mini", "Groq-Llama"])
        
        perf_provider = self.router.get_provider(LLMTier.PERFORMANCE)
        self.assertIn(perf_provider.name, ["Claude-Sonnet", "GPT-4o", "Gemini-Pro"])

    def test_blacklisting_and_fallback(self):
        # Initial state
        p1 = self.router.tiers[LLMTier.ECONOMY][0]
        p2 = self.router.tiers[LLMTier.ECONOMY][1]
        
        self.assertTrue(p1.is_available())
        
        # Report failure on p1
        p1.report_failure()
        self.assertFalse(p1.is_available())
        
        # Router should now return p2
        next_p = self.router.get_provider(LLMTier.ECONOMY)
        self.assertEqual(next_p.name, p2.name)

    async def test_async_generation(self):
        # We need a wrapper to run the async test
        resp = await self.router.generate_text("Hello", tier=LLMTier.ECONOMY)
        self.assertIn("Response from", resp)

class AsyncTestWrapper(unittest.IsolatedAsyncioTestCase):
    async def test_failover_execution(self):
        router = SmartRouter()
        # Mock p1 to fail
        providers = router.tiers[LLMTier.ECONOMY]
        p1 = providers[0]
        p2 = providers[1]
        
        p1.report_failure()
        
        # Should return response from p2
        resp = await router.generate_text("Test", tier=LLMTier.ECONOMY)
        self.assertIn(p2.name, resp)
        self.assertIn("[FALLBACK]", resp)

if __name__ == "__main__":
    unittest.main()
