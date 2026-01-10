from typing import List, Optional, Any
from .provider import BaseProvider

class Agent:
    """
    Represents an autonomous agent with a specific role and goal.
    """
    def __init__(
        self, 
        role: str, 
        goal: str, 
        backstory: str, 
        provider: BaseProvider,
        tools: List[Any] = None,
        verbose: bool = False
    ):
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.provider = provider
        self.tools = tools or []
        self.verbose = verbose
        self.memory = []

    def execute_task(self, task_description: str, context: str = "") -> str:
        """
        Executes a given task using the LLM provider and available tools.
        """
        if self.verbose:
            print(f"[{self.role}] Starting task: {task_description[:50]}...")

        # Construct the prompt
        system_prompt = (
            f"You are {self.role}.\n"
            f"Goal: {self.goal}\n"
            f"Backstory: {self.backstory}\n"
        )
        
        user_prompt = (
            f"Task: {task_description}\n"
            f"Context: {context}\n"
            "Please execute this task to the best of your ability."
        )

        # Basic execution (can be enhanced with ReAct loop later)
        response = self.provider.generate_text(user_prompt, system_prompt=system_prompt)
        
        if self.verbose:
            print(f"[{self.role}] Finished task.")
            
        return response
