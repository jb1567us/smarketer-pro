from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class NodeContext:
    """
    Context passed to every node execution.
    Contains global workflow data, execution ID, and previous step outputs.
    """
    execution_id: str
    workflow_id: str
    global_state: Dict[str, Any] = field(default_factory=dict)
    steps_output: Dict[str, Any] = field(default_factory=dict)
    logger: Any = None

class BaseNode(ABC):
    """
    Standard interface for all Automation Engine nodes.
    Emulates an N8N node structure.
    """
    
    @property
    @abstractmethod
    def node_type(self) -> str:
        """
        Unique identifier for the node type (e.g., 'action.email', 'logic.if').
        """
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """User-friendly name."""
        pass

    def validate_params(self, params: Dict[str, Any]) -> bool:
        """
        Override to provide parameter validation logic.
        Returns True by default.
        """
        return True

    @abstractmethod
    async def execute(self, context: NodeContext, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        The core logic of the node.
        
        Args:
            context: The execution context (access to global state/prev outputs)
            params: Configuration for this specific node instance
            
        Returns:
            Dict containing the output data of this node.
        """
        pass
