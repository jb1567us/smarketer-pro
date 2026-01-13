from typing import Any, Dict
from src.nodes.base import BaseNode, NodeContext
from src.nodes.registry import register_node

class TriggerNode(BaseNode):
    @property
    def node_type(self) -> str:
        return "trigger.manual"

    @property
    def display_name(self) -> str:
        return "Manual Trigger"

    async def execute(self, context: NodeContext, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Acts as a starting point. Passes global state payload through.
        """
        context.logger.info("[TriggerNode] Manual trigger activated.")
        return context.global_state

register_node(TriggerNode())
