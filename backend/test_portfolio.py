import unittest
import os
from backend.database import init_db, get_connection
from backend.portfolio_utils import ReputationScorer, sync_profile

class TestPortfolio(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Ensure DB is initialized
        init_db()

    def test_reputation_scoring(self):
        # High rating, decent reviews
        score_high = ReputationScorer.calculate_score(150, 4.8)
        # Low rating, few reviews
        score_low = ReputationScorer.calculate_score(5, 3.2)
        
        self.assertGreater(score_high, score_low)
        self.assertLessEqual(score_high, 100)
        self.assertGreater(score_low, 0)
        
        # Test logarithmic impact
        score_100 = ReputationScorer.calculate_score(100, 4.0)
        score_1000 = ReputationScorer.calculate_score(1000, 4.0)
        self.assertGreater(score_1000, score_100)

    def test_profile_sync(self):
        name = "Test Business LLC"
        city = "Austin"
        niche = "Plumbers"
        
        # Initial sync
        score = sync_profile(name, niche, city, 50, 4.5)
        
        conn = get_connection()
        c = conn.cursor()
        c.execute("SELECT reputation_score, city FROM company_profiles WHERE name = ?", (name,))
        row = c.fetchone()
        conn.close()
        
        self.assertIsNotNone(row)
        self.assertEqual(row[0], score)
        self.assertEqual(row[1], city)

if __name__ == "__main__":
    unittest.main()
