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

    def is_directory(self, path: str) -> bool:
        """
        Checks if a path is a directory by attempting to list its content.
        """
        try:
            # If we can list it, it's likely a directory
            self.list_files(path)
            return True
        except Exception:
            return False

    def download_file(self, remote_path: str, local_path: str):
        """
        Downloads a file from the server to local path.
        """
        if self.is_directory(remote_path):
            raise ValueError(f"Remote path '{remote_path}' is a directory. Please use `files-compress` to download it as a zip archive.")

        data = self.get_file_content(remote_path)
        content = data.get("content") if isinstance(data, dict) else data
        
        # If content is None, maybe file is empty
        if content is None:
            content = ""
            
        # Write to local
        # If we received string, write as text. If bytes, write key.
        mode = "w" if isinstance(content, str) else "wb"
        encoding = "utf-8" if mode == "w" else None
        
        with open(local_path, mode, encoding=encoding) as f:
            f.write(content)


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

    def compress_files(self, source_paths: list, dest_path: str, type: str = "zip"):
        """
        Compresses files or directories.
        source_paths: list of full paths to compress
        dest_path: full path including filename (e.g., public_html/backup.zip)
        type: zip, tar, gzip, bzip2
        """
        # UAPI Fileman::compress_files
        # 'files' argument is one or more file paths. 
        # 'compress_file_path' is destination.
        
        # We need to correctly pass list of files.
        # UAPI usually accepts multiple keys or comma sep? 
        # Check docs: "files" parameter.
        # Actually standard python request for duplicate keys?
        # Or usually it takes a list in client logic.
        
        # NOTE: UAPI usually expects 'files' as a list argument which requests handles as multiple params with same key
        return self.client.call_uapi("Fileman", "compress_files", compress_file_path=dest_path, type=type, files=source_paths)

    def extract_files(self, source_path: str, dest_path: str):
        """
        Extracts an archive.
        source_path: path to archive
        dest_path: directory to extract to
        """
        return self.client.call_uapi("Fileman", "extract_files", sourcefiles=source_path, path=dest_path)

    def change_permissions(self, path: str, permissions: str):
        """
        Change file permissions (chmod).
        permissions: e.g. "0755" or "0644"
        """
        return self.client.call_uapi("Fileman", "chmod", files=path, permissions=permissions)


