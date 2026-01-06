from typing import List
from .agent import Agent
from .task import Task

class Workflow:
    """
    Orchestrates the execution of a set of tasks by a set of agents.
    """
    def __init__(self, agents: List[Agent], tasks: List[Task], verbose: bool = False):
        self.agents = agents
        self.tasks = tasks
        self.verbose = verbose

    def kickoff(self) -> dict:
        """
        Starts the workflow execution sequentially.
        """
        context = ""
        results = {}
        
        for i, task in enumerate(self.tasks):
            if self.verbose:
                print(f"--- Starting Task {i+1} ---")
                
            result = task.execute(context=context)
            results[f"task_{i}"] = result
            
            # Pass result as context to next task
            context += f"\nPrevious Task Result:\n{result}\n"
            
        return results
