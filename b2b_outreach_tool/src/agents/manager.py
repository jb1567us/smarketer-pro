from .base import BaseAgent
import json


class ManagerAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            role="Manager & Orchestrator",
            goal="Oversee the outreach process, execute tasks via tools, and manage workflows.",
            provider=provider
        )

    def think(self, user_input, intent_history=None, available_tools=None):
        """
        Decides on the next action based on user input.
        """
        tools_desc = (
            "1. run_search(query, niche, profile): Search for leads. 'profile' can be 'default' or custom.\n"
            "2. save_workflow(name): Save the confirmed steps as a workflow.\n"
            "3. list_workflows(): List available saved workflows.\n"
            "4. run_workflow(name): Load and execute a saved workflow.\n"
            "5. chat(message): Just reply to the user if no tool is needed.\n"
        )

        system_prompt = (
            "You are the Manager Agent. You control the B2B Outreach System.\n"
            "Your job is to interpret user requests and call the appropriate tool.\n"
            "If the user wants to do something complex, break it down or ask for details.\n"
            "If the user asks to 'save this' or 'make a workflow', use save_workflow.\n"
            "If the user wants to run a saved process, use run_workflow.\n\n"
            f"Available Tools:\n{tools_desc}\n\n"
            "Return JSON ONLY in this format:\n"
            "{\n"
            "  'tool': 'tool_name',\n"
            "  'params': { ... arguments ... },\n"
            "  'reply': 'Message to user explaining what you are doing'\n"
            "}"
        )
        
        history_str = ""
        if intent_history:
            history_str = f"History:\n{json.dumps(intent_history, indent=2)}\n\n"

        full_prompt = (
            f"{system_prompt}\n\n"
            f"{history_str}"
            f"User Input: {user_input}\n"
        )
        
        return self.provider.generate_json(full_prompt)
