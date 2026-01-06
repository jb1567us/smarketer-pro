from .base import BaseAgent
import json
from utils.agent_registry import list_available_agents
from memory import Memory

class ManagerAgent(BaseAgent):
    def __init__(self, provider=None):
        super().__init__(
            role="Manager & Orchestrator",
            goal="Oversee the outreach process, execute tasks via tools, and manage workflows.",
            provider=provider
        )
        self.memory = Memory()

    def think(self, user_input, intent_history=None, available_tools=None):
        """
        Decides on the next action based on user input.
        """
        agent_list = ", ".join(list_available_agents())
        
        # Get learned context
        memory_context = self.memory.get_context()

        tools_desc = (
            "1. run_search(query, niche, profile): Search for leads. 'profile' can be 'default' or custom.\n"
            "2. save_workflow(name): Save the confirmed steps as a workflow.\n"
            "3. list_workflows(): List available saved workflows.\n"
            "4. run_workflow(name): Load and execute a saved workflow.\n"
            "5. delegate_task(agent_name, instructions): Delegate a specific task to a specialized agent.\n"
            f"   Available Agents: {agent_list}\n"
            "6. chat(message): Just reply to the user if no tool is needed.\n"
        )

        system_prompt = (
            "You are the Manager Agent. You control the B2B Outreach System.\n"
            "Your job is to interpret user requests and call the appropriate tool.\n"
            "If the user wants to do something complex, break it down or ask for details.\n"
            "If the user asks to 'save this' or 'make a workflow', use save_workflow.\n"
            "If the user wants to run a saved process, use run_workflow.\n"
            "If the task requires a specialist (e.g. 'write email', 'analyze SEO', 'create image'), use delegate_task.\n"
            "ALWAYS check your Memory Context to learn from past user preferences.\n\n"
            f"{memory_context}\n\n"
            f"Available Tools:\n{tools_desc}\n\n"
            "Return JSON ONLY in this format:\n"
            "{\n"
            "  'tool': 'tool_name',\n"
            "  'params': { ... arguments ... },\n"
            "  'reply': 'Message to user explaining what you are doing. Mention if you used a preference.'\n"
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
