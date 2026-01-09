
import unittest
import sys
import os
import json
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from database import init_db, save_link_wheel, get_link_wheels, delete_link_wheel

class TestLinkWheelDB(unittest.TestCase):
    def setUp(self):
        # We assume the DB is initialized or we init it safely
        init_db()

    def test_save_and_retrieve(self):
        print("Testing Link Wheel Save/Retrieve...")
        plan = {"tiers": [{"level": 1, "url": "test.com"}]}
        plan_json = json.dumps(plan)
        
        lw_id = save_link_wheel("http://money-site.com", "standard", plan_json)
        self.assertIsNotNone(lw_id)
        
        wheels = get_link_wheels()
        found = False
        for w in wheels:
            if w['id'] == lw_id:
                found = True
                self.assertEqual(w['money_site_url'], "http://money-site.com")
                self.assertEqual(w['strategy'], "standard")
                self.assertEqual(w['tier_plan_json'], plan_json)
                break
        
        self.assertTrue(found, "Saved link wheel not found in DB")
        print("✅ Save & Retrieve Passed")
        
        # Cleanup
        delete_link_wheel(lw_id)
        wheels_after = get_link_wheels()
        self.assertFalse(any(w['id'] == lw_id for w in wheels_after))
        print("✅ Delete Passed")

if __name__ == '__main__':
    unittest.main()
