import unittest
import sqlite3
import asyncio
import os
from unittest.mock import patch
from backend.stealth_utils import SearchRotator, search_rotator
from backend.reflex_exporter import export_static_site
from backend.database import init_db, get_connection, DB_PATH

class TestPhase4(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Create an in-memory database for testing
        self.test_conn = sqlite3.connect(":memory:")
        # Patch BOTH the database module and the module that imports it
        self.patchers = [
            patch("backend.database.get_connection", return_value=self.test_conn),
            patch("backend.reflex_exporter.get_connection", return_value=self.test_conn)
        ]
        for p in self.patchers:
            p.start()
            
        # Manually create the necessary tables for this test
        c = self.test_conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS company_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                last_enriched INTEGER
            )
        ''')
        self.test_conn.commit()

    def tearDown(self):
        for p in self.patchers:
            p.stop()
        self.test_conn.close()

    def test_search_rotation(self):
        # Test 1: Alternating backends
        route1 = search_rotator.get_best_route()
        route2 = search_rotator.get_best_route()
        
        self.assertNotEqual(route1, route2)
        self.assertIn(route1, ["Google", "SearXNG"])
        self.assertIn(route2, ["Google", "SearXNG"])

    async def test_reflex_export_mock(self):
        # The exporter logs to INFO
        success = await export_static_site()
        self.assertTrue(success, "export_static_site returned False")
        
        # Verify dummy file creation
        export_file = os.path.join(os.getcwd(), "static_exports", "last_export.txt")
        self.assertTrue(os.path.exists(export_file), f"Export file missing at {export_file}")

if __name__ == "__main__":
    unittest.main()
