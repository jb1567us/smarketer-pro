import os
import datetime
from pathlib import Path
import inspect

class LegacyKeeper:
    def __init__(self, archive_dir: str = "legacy_archive"):
        self.archive_dir = Path(archive_dir)
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.archive_dir / "graveyard_log.md"
        
        if not self.log_file.exists():
            with open(self.log_file, 'w', encoding='utf-8') as f:
                f.write("# Graveyard Log\n\nTracing deleted logic and moved code.\n\n")

    def archive_code(self, name: str, code_content: str, reason: str = "") -> str:
        """
        Saves a block of code to a file for safekeeping.
        """
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name}_archived_{timestamp}.py"
        filepath = self.archive_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# Archived: {datetime.datetime.now()}\n")
            f.write(f"# Reason: {reason}\n")
            f.write("-" * 40 + "\n\n")
            f.write(code_content)
            
        self._log_entry(f"Archived code '{name}' to {filename}", reason)
        return str(filepath)

    def _log_entry(self, action: str, note: str):
        with open(self.log_file, 'a', encoding='utf-8') as f:
            entry = f"## {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}: {action}\n"
            if note:
                entry += f"> {note}\n\n"
            else:
                entry += "\n"
            f.write(entry)
            
    def log_behavior(self, tag: str, description: str):
        """
        Log a specific behavior/logic that was removed or changed.
        """
        self._log_entry(f"Logic Change: [{tag}]", description)
