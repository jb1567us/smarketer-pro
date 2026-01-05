from .base import BaseAgent

class CustomAgent(BaseAgent):
    def __init__(self, name, role, goal, system_prompt=None, provider=None):
        super().__init__(role=role, goal=goal, provider=provider)
        self.name = name
        self.system_prompt = system_prompt

    def think(self, context, instructions=None):
        """
        Generates a response based on the custom agent's role, goal, and system prompt.
        """
        base_prompt = self.system_prompt if self.system_prompt else ""
        
        system_msg = f"Role: {self.role}\nGoal: {self.goal}\n{base_prompt}\n\n"
        
        full_prompt = f"{system_msg}Context:\n{context}\n\n"
        if instructions:
            full_prompt += f"Instructions:\n{instructions}"
            
        return self.provider.generate_text(full_prompt)
