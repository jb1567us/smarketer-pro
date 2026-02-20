import reflex as rx
import os
import sys

# Add project root and backend directory to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, "backend"))

try:
    from backend.database import init_db, get_connection
    from backend.automation_engine import AutomationEngine
    DB_AVAILABLE = True
    engine = AutomationEngine()
except ImportError:
    DB_AVAILABLE = False
    engine = None

class BaseState(rx.State):
    """Base state for the app."""
    # Global flags
    db_initialized: bool = False
    is_hydrated: bool = True
    is_polling: bool = False
    show_logs: bool = False
    
    # Error Handling
    global_error: str = ""
    error_type: str = ""  # 'warning' | 'error' | 'info' | 'success'
    
    # Global Logs
    server_logs: list[str] = []
    
    def add_log(self, message: str):
        """Append a message to the logs."""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.server_logs.append(log_entry)
        if len(self.server_logs) > 500:
            self.server_logs = self.server_logs[-500:]

    def toggle_logs(self):
        """Toggle log visibility."""
        self.show_logs = not self.show_logs

    def clear_logs(self):
        """Clear log history."""
        self.server_logs = []
        self.add_log("Logs cleared")

    def download_logs(self):
        """Download logs as text file."""
        return rx.download(data=self.logs_text, filename="system_logs.txt")

    def handle_error(self, error: Exception, context: str):
        """Centralized error handler."""
        error_msg = str(error)
        self.global_error = f"{context}: {error_msg}"
        self.error_type = "error"
        self.add_log(f"ERROR in {context}: {error_msg}")

    def clear_error(self):
        """Clears the global error message."""
        self.global_error = ""
        self.error_type = ""

    def show_success(self, message: str):
        """Shows a success message."""
        self.global_error = message
        self.error_type = "success"

    @rx.var
    def logs_text(self) -> str:
        return "\n".join(self.server_logs)

    def handle_ui_action(self, action_name: str):
        """Generic handler for UI actions that aren't yet fully implemented."""
        self.add_log(f"UI Action triggered: {action_name}")
        self.show_success(f"Action '{action_name}' recorded.")
