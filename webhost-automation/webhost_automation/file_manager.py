from .client import CPanelClient

class FileManager:
    def __init__(self, client: CPanelClient):
        self.client = client

    def list_files(self, directory: str = "public_html"):
        """
        Lists files in a given directory using UAPI Fileman.
        """
        # UAPI Fileman::list_files
        # params: dir (path relative to home)
        return self.client.call_uapi("Fileman", "list_files", dir=directory)

    def get_file_content(self, file_path: str):
        """
        Get content of a file (if text).
        UAPI Fileman::get_file_content
        """
        return self.client.call_uapi("Fileman", "get_file_content", file=file_path)

    def upload_file(self, local_path: str, remote_dir: str):
        """
        Uploads a local file to a remote directory.
        UAPI Fileman::upload_files
        """
        import os
        filename = os.path.basename(local_path)
        
        # cPanel UAPI upload is a bit specialized. 
        # Typically requires POST to /execute/Fileman/upload_files 
        # But `upload_files` is effectively the command.
        
        # We need to bypass the standard call_uapi JSON wrapper for binary upload usually?
        # Actually UAPI doc says: POST with multipart/form-data.
        # Key is 'file-1', 'file-2' etc. for files.
        # And 'dir' for destination.
        
        url = f"{self.client.config.cpanel_url}/execute/Fileman/upload_files"
        try:
            with open(local_path, "rb") as f:
                files = {'file-1': (filename, f)}
                data = {'dir': remote_dir}
                
                # We use the session directly to handle multipart upload
                response = self.client.session.post(url, data=data, files=files, timeout=60)
                response.raise_for_status()
                result = response.json()
                
                if result.get("status") == 0:
                     raise Exception(f"Upload failed: {result.get('errors')}")
                return result.get("data")
        except Exception as e:
            raise Exception(f"Upload error: {e}")

    def delete_file(self, remote_path: str):
        """
        Deletes a file or directory.
        UAPI Fileman::fileop check(fileop) -> unlink (delete) or trash
        """
        # Note: double_decode=0 is standard defaults
        # Names are passed as 'files' (or 'file' sometimes depending on ver)
        # UAPI 'Fileman' 'fileop'
        return self.client.call_uapi("Fileman", "fileop", op="unlink", sourcefiles=remote_path)

    def create_directory(self, path: str, name: str):
        """
        Creates a directory.
        path: parent directory
        name: new folder name
        """
        return self.client.call_uapi("Fileman", "mkdir", path=path, name=name)

