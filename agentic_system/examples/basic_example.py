import sys
import os

# Add the parent directory to sys.path to import the package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.agent import Agent
from core.task import Task
from core.workflow import Workflow
from core.provider import BaseProvider

class MockProvider(BaseProvider):
    def generate_text(self, prompt: str, system_prompt: str = None) -> str:
        return f"Mock response for: {prompt[:30]}..."

    def generate_json(self, prompt: str, schema: dict = None) -> dict:
        return {"mock_key": "mock_value"}

def main():
    print("Initializing Mock Provider...")
    provider = MockProvider()

    print("Creating Agents...")
    researcher = Agent(
        role="Researcher",
        goal="Find information",
        backstory="Expert researcher",
        provider=provider,
        verbose=True
    )

    writer = Agent(
        role="Writer",
        goal="Write content",
        backstory="Expert writer",
        provider=provider,
        verbose=True
    )

    print("Creating Tasks...")
    task1 = Task(
        description="Research AI agents",
        expected_output="A list of AI agents",
        agent=researcher
    )

    task2 = Task(
        description="Write a blog post about AI agents",
        expected_output="A blog post",
        agent=writer
    )

    print("Creating Workflow...")
    workflow = Workflow(
        agents=[researcher, writer],
        tasks=[task1, task2],
        verbose=True
    )

    print("Kickoff Workflow...")
    results = workflow.kickoff()
    
    print("\nWorkflow Results:")
    print(results)

if __name__ == "__main__":
    main()
