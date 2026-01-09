import ftplib
import os
from config import config

class FTPManager:
    """
    Manages FTP connections and file operations using configuration from .env/config.py.
    """
    def __init__(self, host=None, user=None, passwd=None, port=21):
        # Load from config if not provided
        ftp_conf = config.get('ftp', {})
        self.host = host or ftp_conf.get('host')
        self.user = user or ftp_conf.get('user')
        self.passwd = passwd or ftp_conf.get('pass')
        self.port = port or int(ftp_conf.get('port', 21))
        self.ftp = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def connect(self):
        """Establishes the FTP connection."""
        if not self.host or not self.user or not self.passwd:
            raise ValueError("FTP credentials not configured. Please set FTP_HOST, FTP_USER, and FTP_PASS in .env")
        
        try:
            print(f"Connecting to FTP: {self.host}:{self.port} as {self.user}...")
            self.ftp = ftplib.FTP()
            self.ftp.connect(self.host, self.port)
            self.ftp.login(self.user, self.passwd)
            print("FTP connection established.")
        except Exception as e:
            print(f"FTP Connection failed: {e}")
            raise

    def disconnect(self):
        """Closes the FTP connection safely."""
        if self.ftp:
            try:
                self.ftp.quit()
            except:
                try:
                    self.ftp.close()
                except:
                    pass
            self.ftp = None
            print("FTP disconnected.")

    def list_files(self, directory=None):
        """Lists files in the current or specified directory."""
        if not self.ftp:
            raise ConnectionError("FTP not connected.")
        
        try:
            if directory:
                self.ftp.cwd(directory)
            
            files = []
            self.ftp.dir(files.append)
            return files
        except Exception as e:
            print(f"FTP List failed: {e}")
            return []

    def upload_file(self, local_path, remote_path):
        """Uploads a local file to the remote path."""
        if not self.ftp:
            raise ConnectionError("FTP not connected.")
        
        if not os.path.exists(local_path):
            raise FileNotFoundError(f"Local file not found: {local_path}")

        try:
            with open(local_path, 'rb') as f:
                self.ftp.storbinary(f'STOR {remote_path}', f)
            print(f"Uploaded: {local_path} -> {remote_path}")
            return True
        except Exception as e:
            print(f"FTP Upload failed: {e}")
            raise

    def download_file(self, remote_path, local_path):
        """Downloads a remote file to the local path."""
        if not self.ftp:
            raise ConnectionError("FTP not connected.")

        try:
            with open(local_path, 'wb') as f:
                self.ftp.retrbinary(f'RETR {remote_path}', f.write)
            print(f"Downloaded: {remote_path} -> {local_path}")
            return True
        except Exception as e:
            print(f"FTP Download failed: {e}")
            raise
