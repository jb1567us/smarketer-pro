from nodes.base import BaseNode, NodeContext
from nodes.registry import register_node
from utils.agent_registry import list_available_agents, get_agent_class
from typing import Any, Dict
from llm import LLMFactory
import traceback

class DynamicAgentNode(BaseNode):
    def __init__(self, agent_key: str):
        self.agent_key = agent_key
        # Pre-fetch metadata if possible, or just default
        self._node_type = f"agent.{agent_key}"

    @property
    def node_type(self) -> str:
        return self._node_type

    @property
    def display_name(self) -> str:
        return f"Agent: {self.agent_key.title()}"

    async def execute(self, context: NodeContext, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes the specific agent.
        """
        context.logger.info(f"[{self.display_name}] Executing...")
        
        try:
            # 1. Instantiate Agent
            agent_cls = get_agent_class(self.agent_key)
            if not agent_cls:
                raise ValueError(f"Agent '{self.agent_key}' class not found.")
                
            provider = LLMFactory.get_provider()
            
            import inspect
            if inspect.isclass(agent_cls):
                agent_instance = agent_cls(provider=provider)
            else:
                agent_instance = agent_cls(provider=provider) # Factory

            # 2. Determine Instruction/Task
            # Workflow might pass 'task', 'instructions', or 'input_variable'
            instructions = params.get("task") or params.get("instructions")
            
            # Handle input variables being passed as main context
            input_var = params.get("input_variable")
            if input_var:
                if input_var in params:
                    # If the variable content is passed in params (by previous node output mapping)
                    context_data = params[input_var]
                else:
                    # Generic fallback
                    context_data = str(params)
            else:
                context_data = params

            # 3. Execute
            result = None
            if hasattr(agent_instance, "think_async"):
                result = await agent_instance.think_async(context_data, instructions)
            else:
                import asyncio
                import functools
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None, 
                    functools.partial(agent_instance.think, context_data, instructions)
                )

            context.logger.info(f"[{self.display_name}] Finished.")
            return result

        except Exception as e:
            context.logger.error(f"Agent Execution Failed: {e}")
            return {"error": str(e), "traceback": traceback.format_exc()}

# --- Dynamic Registration ---
def register_all_agents():
    # Only register standard agents for now to avoid side effects during import time if DB is locked
    # iterating known metadata keys is safer
    from utils.agent_registry import AGENT_METADATA
    
    for key in AGENT_METADATA.keys():
        node = DynamicAgentNode(key)
        register_node(node)

# Execute registration immediately on import
register_all_agents()
