
import json

class WorkflowRecorder:
    def __init__(self):
        self._steps = []

    def log_step(self, tool_name, parameters, description=None):
        """
        Logs a step in the workflow.
        :param tool_name: Name of the tool/function called (e.g., 'run_search')
        :param parameters: Dict of parameters passed to the tool
        :param description: Human readable description
        """
        step = {
            "tool": tool_name,
            "params": parameters,
            "description": description or f"Execute {tool_name}"
        }
        self._steps.append(step)

    def get_workflow(self):
        """Returns the list of recorded steps."""
        return self._steps

    def clear(self):
        """Clears the current recording."""
        self._steps = []

    def load_steps(self, steps):
        """Loads a list of steps (for re-execution or editing)."""
        if isinstance(steps, str):
            try:
                self._steps = json.loads(steps)
            except:
                self._steps = []
        elif isinstance(steps, list):
            self._steps = steps
