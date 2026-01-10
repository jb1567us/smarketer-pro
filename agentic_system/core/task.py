from typing import Optional
from .agent import Agent

class Task:
    """
    Represents a specific unit of work to be performed by an agent.
    """
    def __init__(
        self, 
        description: str, 
        expected_output: str, 
        agent: Optional[Agent] = None
    ):
        self.description = description
        self.expected_output = expected_output
        self.agent = agent
        self.output = None

    def execute(self, context: str = "") -> str:
        """
        Executes the task using the assigned agent.
        """
        if not self.agent:
            raise ValueError("No agent assigned to this task.")
            
        result = self.agent.execute_task(
            task_description=f"{self.description}\nExpected Output: {self.expected_output}",
            context=context
        )
        self.output = result
        return result
