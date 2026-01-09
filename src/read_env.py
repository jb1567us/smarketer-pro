
import os

env_path = "searxng/.env"
if os.path.exists(env_path):
    print(f"Reading {env_path}:")
    with open(env_path, "r") as f:
        print(f.read())
else:
    print(".env not found")
