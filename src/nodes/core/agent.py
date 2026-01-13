from typing import Any, Dict
from src.nodes.base import BaseNode, NodeContext
from src.nodes.registry import register_node
from src.utils.agent_registry import get_agent_class
from src.llm import LLMFactory
import traceback

class AgentNode(BaseNode):
    @property
    def node_type(self) -> str:
        return "core.agent"

    @property
    def display_name(self) -> str:
        return "AI Agent (Delegate)"

    async def execute(self, context: NodeContext, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delegates a task to a named Agent (Researcher, Copywriter, etc).
        Params:
            agent_role (str): The key name of the agent (e.g. 'researcher', 'copywriter').
            instructions (str): The task or question for the agent.
            context_data (any): Optional context to pass to the agent's think() method.
        """
        agent_role = params.get("agent_role")
        instructions = params.get("instructions")
        context_data = params.get("context_data", "")
        
        if not agent_role or not instructions:
             raise ValueError("AgentNode requires 'agent_role' and 'instructions'.")

        context.logger.info(f"[AgentNode] Delegating to: {agent_role}")
        
        try:
            # 1. Get Agent Class/Factory
            agent_cls = get_agent_class(agent_role)
            if not agent_cls:
                raise ValueError(f"Agent '{agent_role}' not found in registry.")
                
            # 2. Instantiate Agent
            # Note: get_agent_class might return a class (standard) or factory (custom)
            provider = LLMFactory.get_provider()
            
            # Check if it's a class or function
            import inspect
            if inspect.isclass(agent_cls):
                agent_instance = agent_cls(provider=provider)
            else:
                agent_instance = agent_cls(provider=provider) # Factory function
            
            # 3. Execute
            # Most agents have a think() method. Some are async (think_async).
            # We prefer async if available, else run sync in executor.
            
            result = None
            if hasattr(agent_instance, "think_async"):
                result = await agent_instance.think_async(context_data, instructions)
            else:
                # Run sync think() in thread to avoid blocking loop
                import asyncio
                import functools
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None, 
                    functools.partial(agent_instance.think, context_data, instructions)
                )
            
            context.logger.info(f"[AgentNode] {agent_role} completed task.")
            return {
                "agent": agent_role,
                "response": result
            }
            
        except Exception as e:
            error_msg = f"Agent Execution Failed: {str(e)}"
            context.logger.error(error_msg)
            return {"error": str(e), "traceback": traceback.format_exc()}

# Register logic
register_node(AgentNode())
