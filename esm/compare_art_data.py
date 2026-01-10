import json

def compare_data(local_path, remote_path):
    with open(local_path, 'r') as f:
        local_data = json.load(f)
    with open(remote_path, 'r') as f:
        remote_data = json.load(f)

    local_ids = {item.get('id') for item in local_data if item.get('id')}
    remote_ids = {item.get('id') for item in remote_data if item.get('id')}

    print(f"Local entries: {len(local_data)}")
    print(f"Remote entries: {len(remote_data)}")
    
    only_local = local_ids - remote_ids
    only_remote = remote_ids - local_ids
    
    print(f"IDs only in local: {only_local}")
    print(f"IDs only in remote: {only_remote}")

if __name__ == "__main__":
    compare_data('c:/sandbox/esm/artwork_data.json', 'c:/sandbox/esm/webhost-automation/remote_artwork_data.json')
