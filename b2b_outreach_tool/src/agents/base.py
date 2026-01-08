from llm import LLMFactory
from utils.memory import memory_manager
from database import save_agent_work_product
from utils.persona_manager import persona_manager
from services.rag_service import rag_service
from utils.voice_manager import VoiceManager
import json
import asyncio
import base64

from utils.logger_service import get_logger

class BaseAgent:
    def __init__(self, role, goal, provider=None):
        self.role = role
        self.goal = goal
        if provider:
            self.provider = provider
        else:
            self.provider = LLMFactory.get_provider()
        self.persona = None
        self.voice_manager = VoiceManager() # Basic TTS
        self.logger = get_logger(self.__class__.__name__)

    def get_expertise(self):
        """Returns the agent's expertise metadata from the registry."""
        from utils.agent_registry import get_agent_metadata
        # Try to find metadata by class name or role-based mapping
        # For simplicity, we assume the agent_name in registry matches subclasses
        name = self.__class__.__name__.lower().replace("agent", "")
        return get_agent_metadata(name)

    def set_persona(self, persona_name):
        """Assigns a persona to the agent."""
        self.persona = persona_manager.get_persona(persona_name)
        if self.persona:
            self.role = self.persona.get('role', self.role)
            self.goal = self.persona.get('goal', self.goal)

    def speak(self, text):
        """Standardized method for agents to speak."""
        self.voice_manager.speak(text)

    def analyze_image(self, image_path, instructions=None):
        """Standardized method for agents to analyze images (Vision)."""
        prompt = instructions or "Describe this image in detail."
        try:
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode("utf-8")
                # We assume the provider supports generate_text with an image_data kwarg
                return self.provider.generate_text(prompt, image_data=image_data)
        except Exception as e:
            self.logger.error(f"[BaseAgent] Error analyzing image: {e}", exc_info=True)
            return f"Error: {e}"

    def retrieve_context(self, query, top_k=3):
        """Retrieves context from the RAG store."""
        return rag_service.get_context(query, top_k=top_k)

    def prompt(self, context, instructions, use_rag=False):
        """
        Constructs the prompt and calls the LLM.
        """
        if use_rag:
            rag_context = self.retrieve_context(instructions)
            if rag_context:
                context = f"{context}\n\nAdditional Knowledge Base Context:\n{rag_context}"

        system_msg = f"Role: {self.role}\nGoal: {self.goal}\n\nCRITICAL: Do NOT hallucinate. Only use provided information or verifiable facts. if you don't know, say 'Unknown'."
        
        if self.persona:
            persona_prompt = persona_manager.get_system_prompt(self.persona['name'])
            if persona_prompt:
                system_msg = f"{persona_prompt}\n\nCRITICAL: Do NOT hallucinate."

        full_prompt = f"{system_msg}\n\nContext:\n{context}\n\nInstructions:\n{instructions}"
        return self.provider.generate_text(full_prompt)

    def generate_json(self, prompt, expect_list=False, **kwargs):
        """
        Calls the LLM to generate JSON and ensures the output matches the expected type (dict or list).
        """
        result = self.provider.generate_json(prompt, **kwargs)
        
        if expect_list:
            if isinstance(result, list):
                return result
            if isinstance(result, dict):
                return [result]
            return []
        else:
            if isinstance(result, dict):
                return result
            if isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], dict):
                    return result[0]
            return {}

    async def generate_json_async(self, prompt, expect_list=False, **kwargs):
        """
        Async version of generate_json.
        """
        result = await self.provider.generate_json_async(prompt, **kwargs)
        
        if expect_list:
            if isinstance(result, list):
                return result
            if isinstance(result, dict):
                return [result]
            return []
        else:
            if isinstance(result, dict):
                return result
            if isinstance(result, list) and len(result) > 0:
                if isinstance(result[0], dict):
                    return result[0]
            return {}

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

    def save_work_product(self, content, task_instruction, tags=None):
        """Saves the agent's work product to the database."""
        return save_agent_work_product(
            agent_role=self.role,
            input_task=task_instruction,
            output_content=str(content), # Ensure string format
            tags=tags
        )

    def save_work(self, content, artifact_type="text", metadata=None):
        """Saves the agent's work product to the database."""
        try:
            from database import save_agent_work
            return save_agent_work(self.role, content, artifact_type, metadata)
        except Exception as e:
            print(f"Error saving agent work: {e}")
            return None

    def get_proxy(self):
        """Standardized method for agents to retrieve a high-quality proxy."""
        try:
            from proxy_manager import proxy_manager
            return proxy_manager.get_proxy()
        except ImportError:
            return None

    def report_proxy_status(self, proxy, success, latency=None):
        """Reports the status of a proxy used by this agent."""
        try:
            from proxy_manager import proxy_manager
            proxy_manager.report_result(proxy, success, latency)
        except ImportError:
            pass
