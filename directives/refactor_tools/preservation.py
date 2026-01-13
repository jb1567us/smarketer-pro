from pathlib import Path
from typing import List, Dict

class PreservationChecklist:
    def __init__(self):
        self.items: List[Dict] = []

    def add_item(self, description: str, critical: bool = True, source_file: str = ""):
        self.items.append({
            "desc": description,
            "critical": critical,
            "source": source_file,
            "checked": False
        })

    def generate_markdown(self) -> str:
        output = ["# Preservation Checklist\n"]
        output.append("Ensure these behaviors are preserved after refactoring.\n")
        
        for i, item in enumerate(self.items):
            prio = "🔴 CRITICAL" if item['critical'] else "🟡 NICE-TO-HAVE"
            output.append(f"- [ ] **{prio}**: {item['desc']}")
            if item['source']:
                output.append(f"  - *Source: {item['source']}*")
        
        return "\n".join(output)

    def save_to_file(self, filepath: str):
        content = self.generate_markdown()
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return filepath
