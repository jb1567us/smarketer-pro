from llm import LLMFactory

class BaseAgent:
    def __init__(self, role, goal, provider=None):
        self.role = role
        self.goal = goal
        if provider:
            self.provider = provider
        else:
            self.provider = LLMFactory.get_provider()

    def prompt(self, context, instructions):
        """
        Constructs the prompt and calls the LLM.
        """
        system_msg = f"Role: {self.role}\nGoal: {self.goal}\n\n"
        full_prompt = f"{system_msg}Context:\n{context}\n\nInstructions:\n{instructions}"
        return self.provider.generate_text(full_prompt)

    async def think_async(self, context):
        """
        To be implemented by subclasses.
        Async version of think.
        """
        raise NotImplementedError("Subclasses must implement think_async()")

    def think(self, context):
        """
        To be implemented by subclasses. 
        Should return the agent's output based on value.
        """
        raise NotImplementedError("Subclasses must implement think()")
