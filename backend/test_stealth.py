import unittest
from backend.stealth_utils import ProxyManager, SystemMonitor, CaptchaHealer

class TestStealthScaling(unittest.TestCase):
    def test_proxy_rotation(self):
        proxies = ["p1", "p2", "p3"]
        pm = ProxyManager(proxies)
        
        self.assertEqual(pm.get_proxy(), "p1")
        self.assertEqual(pm.get_proxy(), "p2")
        self.assertEqual(pm.get_proxy(), "p3")
        self.assertEqual(pm.get_proxy(), "p1") # Rotation check

    def test_captcha_queue(self):
        ch = CaptchaHealer()
        ch.add_to_queue("url1")
        ch.add_to_queue("url2")
        
        self.assertEqual(ch.queue_size, 2)
        task = ch.get_next_task()
        self.assertEqual(task[0], "url1")
        self.assertEqual(ch.queue_size, 1)

    def test_concurrency_logic(self):
        # We can't easily mock psutil for total RAM here without complex mockery,
        # but we can verify the method returns an int.
        concurrency = SystemMonitor.get_recommended_concurrency()
        self.assertIsInstance(concurrency, int)
        self.assertGreaterEqual(concurrency, 1)

if __name__ == "__main__":
    unittest.main()
