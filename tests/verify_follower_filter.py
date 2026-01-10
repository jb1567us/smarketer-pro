
import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.influencer_agent import InfluencerAgent

class TestFollowerFiltering(unittest.TestCase):
    def test_parse_follower_count(self):
        agent = InfluencerAgent()
        
        # Test K
        self.assertEqual(agent._parse_follower_count("10K"), 10000)
        self.assertEqual(agent._parse_follower_count("1.5K"), 1500)
        
        # Test M
        self.assertEqual(agent._parse_follower_count("1M"), 1000000)
        self.assertEqual(agent._parse_follower_count("2.5M"), 2500000)
        
        # Test B (why not)
        self.assertEqual(agent._parse_follower_count("1B"), 1000000000)
        
        # Test Plain Numbers and Commas
        self.assertEqual(agent._parse_follower_count("500"), 500)
        self.assertEqual(agent._parse_follower_count("10,000"), 10000)
        
        # Test Edge Cases
        self.assertEqual(agent._parse_follower_count("Unknown"), 0)
        self.assertEqual(agent._parse_follower_count(None), 0)
        self.assertEqual(agent._parse_follower_count("invalid"), 0)
        
        print("Parser logic verified.")

if __name__ == '__main__':
    unittest.main()
