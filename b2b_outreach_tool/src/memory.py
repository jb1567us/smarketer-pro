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
                self.data = {"preferences": [], "feedback": [], "history": [], "insights": [], "style": {}}
        else:
            self.data = {"preferences": [], "feedback": [], "history": [], "insights": [], "style": {}}
        
        # Ensure new keys exist if loading from old file
        if "insights" not in self.data: self.data["insights"] = []
        if "style" not in self.data: self.data["style"] = {}

    def _save_memory(self):
        with open(self.memory_file, "w") as f:
            json.dump(self.data, f, indent=2)

    def add_insight(self, insight):
        """Adds a learned pattern or insight (e.g. 'User likes to verify leads before copy generation')."""
        if insight not in self.data["insights"]:
            self.data["insights"].append({
                "content": insight,
                "timestamp": datetime.now().isoformat()
            })
            self._save_memory()

    def update_style(self, profile):
        """Updates the learned user style profile."""
        self.data["style"].update(profile)
        self._save_memory()

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
        """Returns a formatted string of user preferences, learned insights, and recent history."""
        prefs = "\n".join([f"- {p}" for p in self.data["preferences"]])
        insights = "\n".join([f"- {i['content']}" for i in self.data["insights"][-5:]])
        style = json.dumps(self.data["style"], indent=2)
        
        recent_feedback = sorted(self.data["feedback"], key=lambda x: x['timestamp'], reverse=True)[:5]
        feedback_str = "\n".join([f"- [{f['tool']}] Rated {f['rating']}/5: {f['comment']}" for f in recent_feedback])

        return (
            f"USER PREFERENCES:\n{prefs}\n\n"
            f"LEARNED INSIGHTS & PATTERNS:\n{insights}\n\n"
            f"USER STYLE PROFILE:\n{style}\n\n"
            f"RECENT FEEDBACK:\n{feedback_str}"
        )
