import os

# Define paths
user_profile = os.environ.get('USERPROFILE')
base_path = os.path.join(user_profile, '.litedock', 'images', 'searxng_searxng_latest', 'usr', 'local', 'searxng')
entrypoint_path = os.path.join(base_path, 'entrypoint.sh')
settings_path = os.path.join(base_path, 'searx', 'settings.yml')

def patch_file(path, search, replace, force_unix_newlines=False):
    if not os.path.exists(path):
        print(f"[WARN] File not found: {path}")
        return

    print(f"Patching {path}...")
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    new_content = content.replace(search, replace)
    
    # Write back
    # If force_unix_newlines is True, we ensure \n is used, not \r\n
    newline_mode = '\n' if force_unix_newlines else None
    
    with open(path, 'w', encoding='utf-8', newline=newline_mode) as f:
        f.write(new_content)
    print(f"Successfully patched {path}")

if __name__ == "__main__":
    # patch settings.yml
    patch_file(settings_path, 'ultrasecretkey', 's3cr3tk3yCHANGEME')
    
    # patch entrypoint.sh - FORCE LF line endings
    # FIX: Call python explicitly to bypass broken shebang/CRLF in granian script
    patch_file(entrypoint_path, 
               '/usr/local/searxng/.venv/bin/granian searx.webapp:app', 
               '/usr/local/searxng/.venv/bin/python3 /usr/local/searxng/.venv/bin/granian --interface wsgi --host 0.0.0.0 --port 8080 searx.webapp:app',
               force_unix_newlines=True)
