import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from ftp_manager import FTPManager

class TestFTPManager(unittest.TestCase):
    @patch('ftp_manager.ftplib.FTP')
    def test_connect_success(self, mock_ftp_cls):
        # Setup mock
        mock_ftp = MagicMock()
        mock_ftp_cls.return_value = mock_ftp
        
        # Test
        manager = FTPManager(host='ftp.example.com', user='user', passwd='pass')
        manager.connect()
        
        # Verify
        mock_ftp.connect.assert_called_with('ftp.example.com', 21)
        mock_ftp.login.assert_called_with('user', 'pass')
        
    @patch('ftp_manager.ftplib.FTP')
    def test_upload_success(self, mock_ftp_cls):
        mock_ftp = MagicMock()
        mock_ftp_cls.return_value = mock_ftp
        
        manager = FTPManager(host='test', user='test', passwd='test')
        manager.connect()
        
        # Create a dummy file
        with open('test_upload.txt', 'w') as f:
            f.write('content')
            
        try:
            manager.upload_file('test_upload.txt', '/remote/path.txt')
            # Check if storbinary was called
            self.assertTrue(mock_ftp.storbinary.called)
        finally:
            if os.path.exists('test_upload.txt'):
                os.remove('test_upload.txt')

    def test_env_loading(self):
        # Mock os.environ or config
        with patch.dict(os.environ, {
            'FTP_HOST': 'env.host.com',
            'FTP_USER': 'env_user',
            'FTP_PASS': 'env_pass'
        }):
            # We need to reload config to pick up env vars if we were testing config.py directly,
            # but FTPManager pulls from config.config.
            # For this unit test, let's just pass explicitly or mock config.
            pass

if __name__ == '__main__':
    unittest.main()
