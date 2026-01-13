import os
from .client import CPanelClient

class FileManager:
    def __init__(self, client: CPanelClient):
        self.client = client

    def list_files(self, directory: str = "public_html"):
        """Lists files in a given directory using UAPI Fileman."""
        return self.client.call_uapi("Fileman", "list_files", dir=directory)

    def get_file_content(self, file_path: str):
        """Get content of a file (if text)."""
        return self.client.call_uapi("Fileman", "get_file_content", file=file_path)

    def is_directory(self, path: str) -> bool:
        """Checks if a path is a directory."""
        try:
            self.list_files(path)
            return True
        except Exception:
            return False

    def upload_file(self, local_path: str, remote_dir: str):
        """Uploads a local file to a remote directory."""
        filename = os.path.basename(local_path)
        url = f"{self.client.config.cpanel_url}/execute/Fileman/upload_files"
        try:
            with open(local_path, "rb") as f:
                files = {'file-1': (filename, f)}
                data = {'dir': remote_dir}
                response = self.client.session.post(url, data=data, files=files, timeout=60)
                response.raise_for_status()
                result = response.json()
                
                if result.get("status") == 0:
                     raise Exception(f"Upload failed: {result.get('errors')}")
                return result.get("data")
        except Exception as e:
            raise Exception(f"Upload error: {e}")

    def delete_file(self, remote_path: str):
        """Deletes a file or directory."""
        return self.client.call_uapi("Fileman", "fileop", op="unlink", sourcefiles=remote_path)

    def create_directory(self, path: str, name: str):
        """Creates a directory."""
        return self.client.call_uapi("Fileman", "mkdir", path=path, name=name)

    def extract_files(self, source_path: str, dest_path: str):
        """Extracts an archive."""
        return self.client.call_uapi("Fileman", "extract_files", sourcefiles=source_path, path=dest_path)
