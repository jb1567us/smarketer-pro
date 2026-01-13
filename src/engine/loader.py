import json
import logging
from typing import Dict, Any

class WorkflowLoader:
    @staticmethod
    def load_from_file(filepath: str) -> Dict[str, Any]:
        """Loads a workflow definition from a JSON file."""
        try:
            with open(filepath, 'r') as f:
                workflow_def = json.load(f)
            
            # Basic Schema Validation
            if "nodes" not in workflow_def:
                raise ValueError("Workflow definition missing 'nodes' list.")
            if "edges" not in workflow_def:
                raise ValueError("Workflow definition missing 'edges' list.")
                
            return workflow_def
        except Exception as e:
            logging.error(f"Failed to load workflow from {filepath}: {e}")
            raise e
