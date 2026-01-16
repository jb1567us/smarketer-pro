import subprocess
import os

def get_large_objects():
    try:
        # Get all objects
        cmd = ["git", "rev-list", "--objects", "--all"]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=r"d:\sandbox\smarketer-pro")
        objects = result.stdout.strip().splitlines()

        print(f"Total objects to scan: {len(objects)}")
        
        large_files = []
        
        # We'll batch check them using git cat-file --batch-check
        # Format: %(objectname) %(objecttype) %(objectsize) %(rest)
        
        input_data = "\n".join([obj.split()[0] for obj in objects])
        
        cmd_batch = ["git", "cat-file", "--batch-check=%(objectname) %(objecttype) %(objectsize)"]
        result_batch = subprocess.run(cmd_batch, input=input_data, capture_output=True, text=True, cwd=r"d:\sandbox\smarketer-pro")
        
        # Map sha back to path
        sha_to_path = {}
        for obj in objects:
            parts = obj.split(maxsplit=1)
            if len(parts) > 1:
                sha_to_path[parts[0]] = parts[1]
        
        for line in result_batch.stdout.splitlines():
            parts = line.split()
            if len(parts) >= 3:
                sha = parts[0]
                obj_type = parts[1]
                size = int(parts[2])
                
                if obj_type == "blob" and size > 1024 * 1024: # Larger than 1MB
                    path = sha_to_path.get(sha, "unknown")
                    large_files.append((size, path, sha))
        
        # Sort by size descending
        large_files.sort(key=lambda x: x[0], reverse=True)
        
        print("\nTop 20 Largest Files in History:")
        for size, path, sha in large_files[:20]:
            print(f"{size / (1024*1024):.2f} MB - {path} ({sha})")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_large_objects()
