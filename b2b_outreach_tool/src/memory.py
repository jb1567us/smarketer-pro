import json
import os
from datetime import datetime

MEMORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "user_memory.json")

class Memory:
    def __init__(self):
        self.memory_file = MEMORY_FILE
        self._load_memory()

    def _load_memory(self):
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r") as f:
                    self.data = json.load(f)
            except:
                self.data = {"preferences": [], "feedback": [], "history": []}
        else:
            self.data = {"preferences": [], "feedback": [], "history": []}

    def _save_memory(self):
        with open(self.memory_file, "w") as f:
            json.dump(self.data, f, indent=2)

    def add_preference(self, preference):
        """Adds a user preference (e.g., 'Prefer polite tone')."""
        if preference not in self.data["preferences"]:
            self.data["preferences"].append(preference)
            self._save_memory()

    def add_feedback(self, tool, result, rating, comment=""):
        """Stores feedback on a specific tool execution."""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "tool": tool,
            "rating": rating, # 1-5
            "comment": comment
        }
        self.data["feedback"].append(entry)
        self._save_memory()

    def get_context(self):
        """Returns a formatted string of user preferences and relevant history."""
        prefs = "\n".join([f"- {p}" for p in self.data["preferences"]])
        
        # Simple recent feedback summary
        recent_feedback = sorted(self.data["feedback"], key=lambda x: x['timestamp'], reverse=True)[:5]
        feedback_str = "\n".join([f"- [{f['tool']}] Rated {f['rating']}/5: {f['comment']}" for f in recent_feedback])

        return (
            f"USER PREFERENCES:\n{prefs}\n\n"
            f"RECENT FEEDBACK:\n{feedback_str}"
        )
