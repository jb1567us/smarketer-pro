
import sys
import os
import unittest
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from database import (
    add_influencer_candidate,
    get_influencer_candidates,
    update_influencer_candidate_status,
    delete_influencer_candidates,
    get_influencer_stats,
    init_db
)

class TestInfluencerCRUD(unittest.TestCase):
    def setUp(self):
        # Ensure DB tables exist
        init_db()
        self.test_handle = f"test_user_{int(time.time())}"
        self.test_candidate = {
            "handle": self.test_handle,
            "platform": "instagram",
            "url": f"https://instagram.com/{self.test_handle}",
            "niche": "interior design",
            "follower_count": 1000,
            "bio_snippet": "Just a test user",
            "engagement_rate": 2.5,
            "status": "new",
            "metadata": '{"test": true}'
        }

    def tearDown(self):
        # Cleanup is handled in test_delete, but just in case
        candidates = get_influencer_candidates(limit=100, platform="instagram")
        to_delete = [c['id'] for c in candidates if self.test_handle in c['handle']]
        if to_delete:
            delete_influencer_candidates(to_delete)

    def test_crud_flow(self):
        # 1. CREATE
        print(f"Adding candidate {self.test_handle}...")
        success = add_influencer_candidate(self.test_candidate)
        self.assertTrue(success, "Failed to add candidate")

        # Verify duplicate prevention
        print("Testing duplicate prevention...")
        success_dup = add_influencer_candidate(self.test_candidate)
        self.assertFalse(success_dup, "Should not allow duplicate URL")

        # 2. READ
        print("Retrieving candidates...")
        results = get_influencer_candidates(limit=10, platform="instagram")
        found = next((c for c in results if c['url'] == self.test_candidate['url']), None)
        self.assertIsNotNone(found, "Candidate not found after addition")
        self.assertEqual(found['handle'], self.test_handle)
        candidate_id = found['id']

        # 3. UPDATE
        print(f"Updating candidate {candidate_id} status...")
        update_success = update_influencer_candidate_status(candidate_id, "approved")
        self.assertTrue(update_success, "Failed to update status")
        
        # Verify update
        updated_results = get_influencer_candidates(limit=1, status="approved")
        updated_candidate = next((c for c in updated_results if c['id'] == candidate_id), None)
        self.assertIsNotNone(updated_candidate, "Updated candidate not found")
        self.assertEqual(updated_candidate['status'], "approved")

        # 4. STATS
        print("Checking stats...")
        stats = get_influencer_stats()
        print(f"Stats: {stats}")
        self.assertTrue(stats.get('approved', 0) > 0, "Stats should reflect approved candidate")

        # 5. DELETE
        print(f"Deleting candidate {candidate_id}...")
        delete_success = delete_influencer_candidates([candidate_id])
        self.assertTrue(delete_success, "Failed to delete candidate")

        # Verify deletion
        final_results = get_influencer_candidates(limit=10, platform="instagram")
        deleted_candidate = next((c for c in final_results if c['id'] == candidate_id), None)
        self.assertIsNone(deleted_candidate, "Candidate should be deleted")

if __name__ == '__main__':
    unittest.main()
