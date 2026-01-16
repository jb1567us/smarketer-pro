from typing import Any, Dict
from nodes.base import BaseNode, NodeContext
from src.nodes.registry import register_node

class DebugNode(BaseNode):
    @property
    def node_type(self) -> str:
        return "core.debug"

    @property
    def display_name(self) -> str:
        return "Debug Log"

    async def execute(self, context: NodeContext, params: Dict[str, Any]) -> Dict[str, Any]:
        message = params.get("message", "No message provided")
        context.logger.info(f"[DebugNode] {message}")
        print(f"--- DEBUG STEP: {message} ---")
        return {"output": message}

class IfNode(BaseNode):
    @property
    def node_type(self) -> str:
        return "core.if"

    @property
    def display_name(self) -> str:
        return "If / Else"

    async def execute(self, context: NodeContext, params: Dict[str, Any]) -> Dict[str, Any]:
        # Simple evaluation logic
        # Supports: "value1", "operator", "value2"
        # Accessing data from context using dot notation "step_1.output"
        
        value1 = params.get("value1")
        operator = params.get("operator", "==")
        value2 = params.get("value2")
        
        # Resolve variables (Simple resolution for now)
        # In real N8N this is complex expression parsing.
        # Here we just look for {{ }} or plain values? 
        # For v1 lets assume direct values.
        
        result = False
        if operator == "==":
            result = (value1 == value2)
        elif operator == "!=":
            result = (value1 != value2)
        elif operator == ">":
            result = (float(value1) > float(value2))
        elif operator == "<":
            result = (float(value1) < float(value2))
            
        context.logger.info(f"[IfNode] {value1} {operator} {value2} = {result}")
        
        return {"branch": "true" if result else "false", "result": result}

# Auto-register on import
register_node(DebugNode())
register_node(IfNode())
