import json
import os
from datetime import datetime

class AgentMemory:
    def __init__(self, file_path="data/agent_memory.json"):
        self.file_path = file_path
        self._ensure_storage()
        self.memory = self._load()

    def _ensure_storage(self):
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump({}, f)

    def _load(self):
        try:
            with open(self.file_path, 'r') as f:
                return json.load(f)
        except Exception:
            return {}

    def _save(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.memory, f, indent=4)

    def store(self, agent_role, key, content, metadata=None):
        """Stores a fact or observation."""
        if agent_role not in self.memory:
            self.memory[agent_role] = {}
        
        self.memory[agent_role][key] = {
            "content": content,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat()
        }
        self._save()

    def recall(self, agent_role, key=None):
        """Recalls facts for a specific agent or key."""
        role_memory = self.memory.get(agent_role, {})
        if key:
            return role_memory.get(key)
        return role_memory

    def search(self, query):
        """Simple keyword search across all agent memories."""
        results = []
        q = query.lower()
        for role, entries in self.memory.items():
            for key, data in entries.items():
                if q in key.lower() or q in str(data['content']).lower():
                    results.append({"role": role, "key": key, "data": data})
        return results

# Singleton instance
memory_manager = AgentMemory()
