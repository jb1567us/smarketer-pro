from llm import LLMFactory
from utils.memory import memory_manager

class BaseAgent:
    def __init__(self, role, goal, provider=None):
        self.role = role
        self.goal = goal
        
        # Centralized Logging
        from utils.logger_service import get_logger
        self.logger = get_logger(self.role.replace(" ", "_"))
        
        if provider:
            self.provider = provider
        else:
            self.provider = LLMFactory.get_provider()
            
        self.context = None

    def set_context(self, context):
        """Sets the Hub-provided PromptContext for this agent."""
        self.context = context

    def report_to_hub(self, status, details=None):
        """
        Standardized hook for agents to report progress back to the Hub.
        """
        from src.prompt_engine.models import PromptContext
        msg = f"📡 [Hub-Sync] {self.role}: {status}"
        if details:
            msg += f" - {details}"
        self.logger.info(msg)
        # In a full MCP implementation, this would call the report_mission_progress tool

    def prompt(self, context, instructions):
        """
        Constructs the prompt and calls the LLM.
        """
        system_msg = f"Role: {self.role}\nGoal: {self.goal}\n\nCRITICAL: Do NOT hallucinate. Only use provided information or verifiable facts. if you don't know, say 'Unknown'."
        full_prompt = f"{system_msg}\n\nContext:\n{context}\n\nInstructions:\n{instructions}"
        return self.provider.generate_text(full_prompt)

    async def think_async(self, context, instructions=None):
        """
        To be implemented by subclasses.
        Async version of think.
        """
        raise NotImplementedError("Subclasses must implement think_async()")

    def think(self, context, instructions=None):
        """
        To be implemented by subclasses. 
        Should return the agent's output based on value.
        """
        raise NotImplementedError("Subclasses must implement think()")

    def tune(self, context, previous_response, instructions, history=None):
        """
        Refines the previous output based on feedback.
        """
        system_msg = f"Role: {self.role}\nGoal: {self.goal}\n\nCRITICAL: Do NOT hallucinate."
        history_str = f"\n\nConversation History:\n{history}" if history else ""
        full_prompt = (
            f"{system_msg}"
            f"Original Context:\n{context}\n\n"
            f"Previous Output:\n{previous_response}\n\n"
            f"{history_str}\n\n"
            f"Tuning Instructions:\n{instructions}\n\n"
            f"Please update the output based on these instructions."
        )
        return self.provider.generate_text(full_prompt)

    def discuss(self, context, previous_response, message, history=None):
        """
        Discusses the output without committing to a new version.
        """
        system_msg = f"Role: {self.role}\nGoal: {self.goal}\n\nYou are having a discussion about the output you just generated. Do NOT generate a new version of the full output yet unless specifically asked to 'apply' or 'commit'. Just chat and provide guidance/answers. CRITICAL: Do NOT hallucinate."
        history_str = f"\n\nConversation History:\n{history}" if history else ""
        full_prompt = (
            f"{system_msg}"
            f"Original Context:\n{context}\n\n"
            f"Current Output:\n{previous_response}\n\n"
            f"{history_str}\n\n"
            f"User Question/Feedback:\n{message}"
        )
        return self.provider.generate_text(full_prompt)

    def remember(self, key, content, metadata=None):
        """Stores a fact for this agent."""
        memory_manager.store(self.role, key, content, metadata)

    def recall(self, key=None):
        """Recalls facts for this agent."""
        return memory_manager.recall(self.role, key)
